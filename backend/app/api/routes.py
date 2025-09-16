from flask import jsonify, request
from app.api import api_bp
from app.extensions import db
from app.api.models import Survey, Question, Option, SurveyResponse, QuestionResponse

@api_bp.route('/surveys', methods=['GET'])
def get_surveys():
    surveys = Survey.query.all()
    result = []
    for survey in surveys:
        survey_data = survey.to_dict()
        result.append(survey_data)
    return jsonify(result)

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
                    response_info['response'] = option.text if option else 'Unknown option'
                    response_info['option_id'] = qr.option_id
                else:
                    response_info['response'] = 'No response'
            
            processed_responses.append(response_info)
        
        response_data['question_responses'] = processed_responses
        result.append(response_data)
    
    return jsonify(result)

@api_bp.route('/submit', methods=['POST'])
def submit_survey():
    data = request.get_json()
    survey_id = data.get('survey_id')
    responses = data.get('responses', {})
    
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