from app.extensions import db
from datetime import datetime

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to questions
    questions = db.relationship('Question', backref='survey', lazy=True, cascade='all, delete-orphan')
    
    # Relationship to responses
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response_count': len(self.responses)
        }

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1: single choice, 2: multiple choice, 3: text
    required = db.Column(db.Boolean, nullable=False, default=False)  # False: not required, True: required
    order = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationship to options
    options = db.relationship('Option', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'text': self.text,
            'type': self.type,
            'required': self.required,
            'order': self.order,
            'options': [o.to_dict() for o in self.options]
        }

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
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
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to question responses
    question_responses = db.relationship('QuestionResponse', backref='survey_response', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
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