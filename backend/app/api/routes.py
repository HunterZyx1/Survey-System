from flask import jsonify, request
from app.api import api_bp
from app.extensions import db
from app.api.models import User, Survey, Question, Option, SurveyResponse, QuestionResponse
import jwt
import datetime
from functools import wraps
import os

# 密钥用于JWT token签名
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            # 移除Bearer前缀
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # 验证输入
    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # 创建新用户
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # 生成token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict()
    }), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 验证输入
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # 生成token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })

@api_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    # 只有管理员可以获取所有用户列表
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    
    users = User.query.all()
    result = []
    for user in users:
        result.append(user.to_dict())
    return jsonify(result)

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    # 用户只能查看自己的信息，管理员可以查看所有用户信息
    if current_user.id != user_id and not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    # 用户只能更新自己的信息，管理员可以更新所有用户信息
    if current_user.id != user_id and not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 更新用户信息
    if 'username' in data:
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # 检查邮箱是否已存在
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Email already exists'}), 400
        user.email = data['email']
    
    if 'is_admin' in data:
        # 只有管理员可以更改用户权限
        if current_user.is_admin:
            user.is_admin = data['is_admin']
        else:
            return jsonify({'message': 'Permission denied'}), 403
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    # 用户不能删除自己，只有管理员可以删除用户
    if current_user.id == user_id:
        return jsonify({'message': 'You cannot delete yourself'}), 400
    
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@api_bp.route('/surveys', methods=['GET'])
def get_surveys():
    surveys = Survey.query.all()
    result = []
    for survey in surveys:
        survey_data = survey.to_dict()
        result.append(survey_data)
    return jsonify(result)

@api_bp.route('/survey-stats', methods=['GET'])
def get_survey_stats():
    total_surveys = Survey.query.count()
    published_surveys = Survey.query.filter_by(is_published=True).count()
    
    # 计算总响应数
    total_responses = db.session.query(db.func.sum(
        db.session.query(db.func.count(SurveyResponse.id))
        .filter(SurveyResponse.survey_id == Survey.id)
        .correlate(Survey)
        .as_scalar()
    )).scalar() or 0
    
    return jsonify({
        'total_surveys': total_surveys,
        'published_surveys': published_surveys,
        'total_responses': total_responses
    })

@api_bp.route('/surveys', methods=['POST'])
def create_survey():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    questions = data.get('questions', [])
    
    # Create new survey
    survey = Survey(title=title, description=description)
    db.session.add(survey)
    db.session.flush()  # Get the ID of the new survey
    
    # Create each question
    for i, question_data in enumerate(questions):
        text = question_data.get('text')
        type = question_data.get('type')
        required = question_data.get('required', False)
        options = question_data.get('options', [])
        
        # Create new question
        question = Question(
            survey_id=survey.id,
            text=text,
            type=type,
            required=required,
            order=i
        )
        db.session.add(question)
        db.session.flush()  # Get the ID of the new question
        
        # Create options for the question
        for j, option_text in enumerate(options):
            option = Option(
                question_id=question.id,
                text=option_text,
                order=j
            )
            db.session.add(option)
    
    # Commit all changes
    db.session.commit()
    
    # Return the created survey with its questions and options
    survey_data = survey.to_dict()
    survey_data['questions'] = [q.to_dict() for q in survey.questions]
    
    return jsonify(survey_data), 201

@api_bp.route('/surveys/<int:survey_id>', methods=['GET'])
def get_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    survey_data = survey.to_dict()
    survey_data['questions'] = [q.to_dict() for q in survey.questions]
    return jsonify(survey_data)

@api_bp.route('/surveys/<int:survey_id>', methods=['PUT'])
def update_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    data = request.get_json()
    
    # Update survey fields
    survey.title = data.get('title', survey.title)
    survey.description = data.get('description', survey.description)
    survey.is_published = data.get('is_published', survey.is_published)
    
    # Update questions if provided
    if 'questions' in data:
        questions_data = data.get('questions', [])
        
        # Delete existing questions (cascade will delete options)
        for question in survey.questions:
            db.session.delete(question)
        
        # Create new questions
        for i, question_data in enumerate(questions_data):
            text = question_data.get('text')
            type = question_data.get('type')
            required = question_data.get('required', False)
            options = question_data.get('options', [])
            
            # Create new question
            question = Question(
                survey_id=survey.id,
                text=text,
                type=type,
                required=required,
                order=i
            )
            db.session.add(question)
            db.session.flush()  # Get the ID of the new question
            
            # Create options for the question
            for j, option_text in enumerate(options):
                option = Option(
                    question_id=question.id,
                    text=option_text,
                    order=j
                )
                db.session.add(option)
    
    # Update timestamp
    survey.updated_at = db.func.current_timestamp()
    
    # Commit all changes
    db.session.commit()
    
    # Return the updated survey
    survey_data = survey.to_dict()
    survey_data['questions'] = [q.to_dict() for q in survey.questions]
    
    return jsonify(survey_data)

@api_bp.route('/surveys/<int:survey_id>', methods=['DELETE'])
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    return jsonify({'message': 'Survey deleted successfully'}), 200

@api_bp.route('/surveys/<int:survey_id>/publish', methods=['POST'])
def publish_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    survey.is_published = True
    survey.updated_at = db.func.current_timestamp()
    db.session.commit()
    return jsonify({'message': 'Survey published successfully', 'survey': survey.to_dict()}), 200

@api_bp.route('/surveys/<int:survey_id>/unpublish', methods=['POST'])
def unpublish_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    survey.is_published = False
    survey.updated_at = db.func.current_timestamp()
    db.session.commit()
    return jsonify({'message': 'Survey unpublished successfully', 'survey': survey.to_dict()}), 200

@api_bp.route('/published-surveys', methods=['GET'])
def get_published_surveys():
    surveys = Survey.query.filter_by(is_published=True).all()
    result = []
    for survey in surveys:
        survey_data = survey.to_dict()
        survey_data['questions'] = [q.to_dict() for q in survey.questions]
        result.append(survey_data)
    return jsonify(result)

@api_bp.route('/survey-responses/<int:survey_id>', methods=['GET'])
def get_survey_responses(survey_id):
    # Get all responses for a specific survey
    survey_responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
    result = []
    
    # Get the survey to access questions and options
    survey = Survey.query.get_or_404(survey_id)
    questions_dict = {q.id: q for q in survey.questions}
    options_dict = {}
    for question in survey.questions:
        options_dict.update({o.id: o for o in question.options})
    
    for response in survey_responses:
        response_data = response.to_dict()
        
        # Get all question responses for this survey response
        question_responses = QuestionResponse.query.filter_by(survey_response_id=response.id).all()
        
        # Process question responses to make them more readable
        processed_responses = []
        for qr in question_responses:
            question = questions_dict.get(qr.question_id)
            if not question:
                continue
                
            response_info = {
                'question_id': qr.question_id,
                'question_text': question.text,
                'question_type': question.type
            }
            
            if question.type == 3:  # Text question
                response_info['response'] = qr.text_response
            else:  # Choice question
                if qr.option_id:
                    option = options_dict.get(qr.option_id)
                    # 如果有文本响应，说明是"其他"选项
                    if qr.text_response:
                        # 如果选项文本是"其他"，则只显示用户输入的内容
                        if option and option.text == "其他":
                            response_info['response'] = qr.text_response
                        else:
                            response_info['response'] = f"{option.text}: {qr.text_response}" if option else f"Other: {qr.text_response}"
                    else:
                        response_info['response'] = option.text if option else 'Unknown option'
                    response_info['option_id'] = qr.option_id
                else:
                    response_info['response'] = 'No response'
            
            processed_responses.append(response_info)
        
        response_data['question_responses'] = processed_responses
        result.append(response_data)
    
    return jsonify(result)

@api_bp.route('/survey-responses/<int:response_id>', methods=['DELETE'])
def delete_survey_response(response_id):
    # Get the survey response
    survey_response = SurveyResponse.query.get_or_404(response_id)
    
    # Delete the survey response (cascade will delete question responses)
    db.session.delete(survey_response)
    db.session.commit()
    
    return jsonify({'message': 'Survey response deleted successfully'}), 200

@api_bp.route('/submit', methods=['POST'])
def submit_survey():
    data = request.get_json()
    survey_id = data.get('survey_id')
    responses = data.get('responses', {})
    other_texts = data.get('otherTexts', {})  # 获取其他选项文本
    
    # Create a new survey response
    survey_response = SurveyResponse(survey_id=survey_id)
    db.session.add(survey_response)
    db.session.flush()  # Get the ID of the new survey response
    
    # Save each question response
    for question_id, response in responses.items():
        # Check if this is a multi-choice question (handled differently in frontend)
        if isinstance(question_id, str) and '-' in question_id:
            # This is a multi-choice question, handled separately
            continue
            
        # Convert question_id to integer
        try:
            q_id = int(question_id)
        except ValueError:
            continue
            
        # Get the question to determine its type
        question = Question.query.get(q_id)
        if not question:
            continue
            
        # Create question response based on question type
        if question.type == 3:  # Text question
            question_response = QuestionResponse(
                survey_response_id=survey_response.id,
                question_id=q_id,
                text_response=response
            )
        else:  # Choice question (single or multiple)
            # Handle multiple choice responses
            if isinstance(response, list):
                # Multiple choice - create a response for each selected option
                for option_id in response:
                    try:
                        opt_id = int(option_id)
                        # 检查是否是"其他"选项并包含文本
                        other_text_key = f"{q_id}-{opt_id}"
                        if other_text_key in other_texts and other_texts[other_text_key]:
                            question_response = QuestionResponse(
                                survey_response_id=survey_response.id,
                                question_id=q_id,
                                option_id=opt_id,
                                text_response=other_texts[other_text_key]  # 保存其他选项文本
                            )
                        else:
                            question_response = QuestionResponse(
                                survey_response_id=survey_response.id,
                                question_id=q_id,
                                option_id=opt_id
                            )
                        db.session.add(question_response)
                    except ValueError:
                        continue
                continue  # Skip the db.session.add at the end of the loop
            else:  # Single choice
                try:
                    option_id = int(response)
                    # 检查是否是"其他"选项并包含文本
                    other_text_key = f"{q_id}"
                    if other_text_key in other_texts and other_texts[other_text_key]:
                        question_response = QuestionResponse(
                            survey_response_id=survey_response.id,
                            question_id=q_id,
                            option_id=option_id,
                            text_response=other_texts[other_text_key]  # 保存其他选项文本
                        )
                    else:
                        question_response = QuestionResponse(
                            survey_response_id=survey_response.id,
                            question_id=q_id,
                            option_id=option_id
                        )
                except ValueError:
                    continue
        
        db.session.add(question_response)
    
    # Handle multi-choice questions (from the frontend implementation)
    for question_id, selected_options in data.get('selectedOptions', {}).items():
        try:
            q_id = int(question_id)
        except ValueError:
            continue
            
        # Create a response for each selected option
        for option_id in selected_options:
            try:
                opt_id = int(option_id)
                # 检查是否是"其他"选项并包含文本
                other_text_key = f"{q_id}-{opt_id}"
                if other_text_key in other_texts and other_texts[other_text_key]:
                    question_response = QuestionResponse(
                        survey_response_id=survey_response.id,
                        question_id=q_id,
                        option_id=opt_id,
                        text_response=other_texts[other_text_key]  # 保存其他选项文本
                    )
                else:
                    question_response = QuestionResponse(
                        survey_response_id=survey_response.id,
                        question_id=q_id,
                        option_id=opt_id
                    )
                db.session.add(question_response)
            except ValueError:
                continue
    
    # Commit all changes
    db.session.commit()
    
    return jsonify({'message': 'Survey submitted successfully', 'survey_response_id': survey_response.id})