from sqlalchemy.orm import sessionmaker
from seekingalpha_crawler.models import Companies, db_connect, \
    create_table, Transcripts, InternalParticipants, ExternalParticipants,\
    QA, QADialogue, Presentation, PresentationDialogue


class saveToSqlite(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.session = sessionmaker(bind=engine)()

    def process_item(self, item, spider):
        session = self.session

        # Company details
        cur_stock = item.get('stock', None)
        cur_company_id = session.query(Companies.id).filter(
                Companies.stock == cur_stock).first()
        if not cur_company_id:
            company = Companies()
            company.company_name = item.get('company_name', None)
            company.stock = cur_stock
            session.add(company)
            self.commit_func(session)
            cur_company_id = company.id
        else:
            cur_company_id = cur_company_id[0]

        # Transcripts
        transcript = Transcripts()
        transcript.report_id = item.get('report_id', None)
        transcript.published_quarter = item.get('published_quarter', None)
        transcript.date_published = item.get('date_published', None)
        transcript.article_url = item.get('article_url', None)
        transcript.audio_call_url = item.get('audio_call_url', None)
        transcript.article_title = item.get('article_title', None)
        transcript.company_id = cur_company_id
        session.add(transcript)
        self.commit_func(session)

        transcript_id = transcript.id
        # Internal participants
        self.internal_participants(item, session, transcript_id)

        # External participants
        self.external_participants(item, session, transcript_id)

        # Question answers
        qa = QA()
        qa.transcript_id = transcript_id
        session.add(qa)
        self.commit_func(session)

        # Question answer dialogues
        self.qa_dialog(item, session, qa.id, transcript_id)

        # Presentation
        pr = Presentation()
        pr.transcript_id = transcript_id
        session.add(pr)
        self.commit_func(session)

        # Presentatin dialogues
        self.presentation_dialog(item, session, pr.id, transcript_id)

        return item

    def commit_func(self, session):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def internal_participants(self, item, session, transcript_id):

        # include operator
        company_participants = InternalParticipants()
        company_participants.transcript_id = transcript_id
        company_participants.company = item.get('company_name', None)
        company_participants.name = 'Operator'
        company_participants.role = 'Monitors call'
        session.add(company_participants)
        self.commit_func(session)

        # add company participants.
        participants = item.get('company_participants', None)
        for participant in participants:
            company_participants = InternalParticipants()
            company_participants.transcript_id = transcript_id
            company_participants.company = item.get('company_name', None)
            company_participants.name = str(participant[0].strip())
            company_participants.role = participant[1]
            session.add(company_participants)
            self.commit_func(session)

    def external_participants(self, item, session, transcript_id):

        participants = item.get('external_participants', None)
        for participant in participants:
            external_participants = ExternalParticipants()
            external_participants.transcript_id = transcript_id
            external_participants.name = str(participant[0].strip())
            external_participants.company = participant[1]
            session.add(external_participants)
            self.commit_func(session)

    def qa_dialog(self, item, session, qa_id, transcript_id):

        qas = item.get('question_answers', None)
        for qa in qas:
            qa_dialog = QADialogue()
            qa_dialog.qa_id = qa_id
            qa_dialog.dialogue = qa[1]

            internal_person_id = session.query(
                    InternalParticipants.id).filter(
                    InternalParticipants.name == qa[0],
                    InternalParticipants.transcript_id == transcript_id
                    ).first()

            if internal_person_id:
                qa_dialog.internal_person_id = internal_person_id[0]

            else:
                external_person_id = session.query(
                        ExternalParticipants.id).filter(
                        ExternalParticipants.name == qa[0],
                        ExternalParticipants.transcript_id == transcript_id).\
                        first()

                if external_person_id:
                    qa_dialog.external_person_id = external_person_id[0]

            session.add(qa_dialog)
        self.commit_func(session)

    def presentation_dialog(self, item, session, pr_id, transcript_id):

        ect = item.get('earning_call_talk', None)
        for ec in ect:
            pr_dialog = PresentationDialogue()
            pr_dialog.presentation_id = pr_id
            pr_dialog.dialogue = ec[1]
            internal_person_id = session.query(
                        InternalParticipants.id).filter(
                        InternalParticipants.name == ec[0],
                        InternalParticipants.transcript_id == transcript_id
                        ).first()

            if internal_person_id:
                pr_dialog.internal_person_id = internal_person_id[0]
            session.add(pr_dialog)
        self.commit_func(session)

    def close_spider(self, spider):
        """Discard the database pool on spider close"""
        self.session.close()
