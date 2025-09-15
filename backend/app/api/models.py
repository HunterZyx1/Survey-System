from app.extensions import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1: single choice, 2: multiple choice, 3: text
    required = db.Column(db.Boolean, nullable=False, default=False)  # False: not required, True: required
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'type': self.type,
            'required': self.required
        }

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    question = db.relationship('Question', backref=db.backref('options', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'text': self.text,
            'order': self.order
        }

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat()
        }

class QuestionResponse(db.Model):
    __tablename__ = 'question_responses'
    id = db.Column(db.Integer, primary_key=True)
    survey_response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)  # For choice questions
    text_response = db.Column(db.Text, nullable=True)  # For text questions
    
    # Relationships
    survey_response = db.relationship('SurveyResponse', backref=db.backref('question_responses', lazy=True))
    question = db.relationship('Question')
    option = db.relationship('Option')
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_response_id': self.survey_response_id,
            'question_id': self.question_id,
            'option_id': self.option_id,
            'text_response': self.text_response
        }