from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, Text)
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(
        get_project_settings().get('SQLITE_CONNECTION_STRING'))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


def check_duplicate_article(report_id):
    engine = db_connect()
    create_table(engine)
    session = sessionmaker(bind=engine)()
    article_present = session.query(Transcripts).filter(
        Transcripts.report_id == report_id).first()
    if article_present:
        return True
    else:
        return False


class Companies(DeclarativeBase):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column('company_name', Text())
    stock = Column('stock', Text(), unique=True)


class Transcripts(DeclarativeBase):
    __tablename__ = 'transcripts'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column('report_id', Text(), unique=True)
    published_quarter = Column('published_quarter', Text())
    date_published = Column('date_published', Text())
    article_url = Column('article_url', Text())
    audio_call_url = Column('audio_call_url', Text())
    article_title = Column('article_title', Text())
    company_id = Column('company_id', Text())


class InternalParticipants(DeclarativeBase):
    __tablename__ = 'internal_participants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column('name', Text())
    company = Column('company', Text())
    role = Column('role', Text())
    transcript_id = Column(Integer, ForeignKey('transcripts.id'),
                           index=True)


class ExternalParticipants(DeclarativeBase):
    __tablename__ = 'external_participants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column('name', Text())
    company = Column('company', Text())
    transcript_id = Column(Integer, ForeignKey('transcripts.id'),
                           index=True)


class QA(DeclarativeBase):
    __tablename__ = 'question_answers'

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey('transcripts.id'),
                           index=True)


class QADialogue(DeclarativeBase):
    __tablename__ = 'question_answer_dialogues'

    id = Column(Integer, primary_key=True, index=True)
    qa_id = Column(Integer, ForeignKey('question_answers.id'),
                   index=True)
    internal_person_id = Column('internal_person_id', ForeignKey(
                        'internal_participants.id'), index=True)
    external_person_id = Column('external_person_id', ForeignKey(
                        'external_participants.id'), index=True)
    dialogue = Column('dialogue', Text())


class Presentation(DeclarativeBase):
    __tablename__ = 'presentations'

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey('transcripts.id'),
                           index=True)


class PresentationDialogue(DeclarativeBase):
    __tablename__ = 'presentation_dialogues'

    id = Column(Integer, primary_key=True, index=True)
    presentation_id = Column(Integer, ForeignKey('presentations.id'),
                             index=True)
    internal_person_id = Column(Integer, ForeignKey(
                        'internal_participants.id'), index=True)
    dialogue = Column('dialogue', Text())
