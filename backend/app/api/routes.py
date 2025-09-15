from flask import jsonify, request
from app.api import api_bp
from app.extensions import db
from app.api.models import Question, Option, SurveyResponse, QuestionResponse

@api_bp.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    result = []
    for q in questions:
        question_data = q.to_dict()
        question_data['options'] = [o.to_dict() for o in q.options]
        result.append(question_data)
    return jsonify(result)

@api_bp.route('/submit', methods=['POST'])
def submit_survey():
    data = request.get_json()
    responses = data.get('responses', {})
    
    # Create a new survey response
    survey_response = SurveyResponse()
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