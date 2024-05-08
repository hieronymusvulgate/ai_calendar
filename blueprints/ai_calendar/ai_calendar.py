from flask import Blueprint, render_template, redirect, url_for
from blueprints.user_authentication.user_authentication import *
import math
from datetime import date

ai_calendar_bp = Blueprint('ai_calendar', __name__, template_folder='templates')

class SubjectForm(FlaskForm):
    subject = StringField('Subject', validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add Subject')

class FreetimeForm(FlaskForm):
    freetime = SelectField('Freetime', choices=[
                                                ('Hourly'),
                                                ('00:00 - 01:00'), 
                                                ('01:00 - 02:00'), 
                                                ('02:00 - 03:00'), 
                                                ('03:00 - 04:00'),
                                                ('04:00 - 05:00'),
                                                ('05:00 - 06:00'),
                                                ('06:00 - 07:00'),
                                                ('07:00 - 08:00'),
                                                ('08:00 - 09:00'),
                                                ('09:00 - 10:00'),
                                                ('10:00 - 11:00'),
                                                ('11:00 - 12:00'),
                                                ('12:00 - 13:00'),
                                                ('13:00 - 14:00'),
                                                ('14:00 - 15:00'),
                                                ('15:00 - 16:00'),
                                                ('16:00 - 17:00'),
                                                ('17:00 - 18:00'),
                                                ('18:00 - 19:00'),
                                                ('19:00 - 20:00'),
                                                ('20:00 - 21:00'),
                                                ('21:00 - 22:00'),
                                                ('22:00 - 23:00'),
                                                ('23:00 - 00:00'),
                                                ('Half Hourly'),
                                                ('00:00 - 00:30'),
                                                ('00:30 - 01:00'),
                                                ('01:00 - 01:30'),
                                                ('01:30 - 02:00'),
                                                ('02:00 - 02:30'),
                                                ('02:30 - 03:00'),
                                                ('03:00 - 03:30'),
                                                ('03:30 - 04:00'),
                                                ('04:00 - 04:30'),
                                                ('04:30 - 05:00'),
                                                ('05:00 - 05:30'),
                                                ('05:30 - 06:00'),
                                                ('06:00 - 06:30'),
                                                ('06:30 - 07:00'),
                                                ('07:00 - 07:30'),
                                                ('07:30 - 08:00'),
                                                ('08:00 - 08:30'),
                                                ('08:30 - 09:00'),
                                                ('09:00 - 09:30'),
                                                ('09:30 - 10:00'),
                                                ('10:00 - 10:30'),
                                                ('10:30 - 11:00'),
                                                ('11:00 - 11:30'),
                                                ('11:30 - 12:00'),
                                                ('12:00 - 12:30'),
                                                ('12:30 - 13:00'),
                                                ('13:00 - 13:30'),
                                                ('13:30 - 14:00'),
                                                ('14:00 - 14:30'),
                                                ('14:30 - 15:00'),
                                                ('15:00 - 15:30'),
                                                ('15:30 - 16:00'),
                                                ('16:00 - 16:30'),
                                                ('16:30 - 17:00'),
                                                ('17:00 - 17:30'),
                                                ('17:30 - 18:00'),
                                                ('18:00 - 18:30'),
                                                ('18:30 - 19:00'),
                                                ('19:00 - 19:30'),
                                                ('19:30 - 20:00'),
                                                ('20:00 - 20:30'),
                                                ('20:30 - 21:00'),
                                                ('21:00 - 21:30'),
                                                ('21:30 - 22:00'),
                                                ('22:00 - 22:30'),
                                                ('22:30 - 23:00'),
                                                ('23:00 - 23:30'),
                                                ('23:30 - 00:00')
                                                ])
    submit = SubmitField('Add Freetime')

@ai_calendar_bp.route('/')
@login_required
def ai_calendar():
    assignments = Assignments.query.filter_by(user_id=current_user.id).all()
    pro_token = current_user.pro_token
    if pro_token >= 224:
        current_user.optimizer = 10
    elif pro_token >= 112:
        current_user.optimizer = 9
    elif pro_token >= 56:
        current_user.optimizer = 8
    elif pro_token >= 28:
        current_user.optimizer = 7
    elif pro_token >= 14:
        current_user.optimizer = 6
    elif pro_token >= 7:
        current_user.optimizer = 5
    db.session.commit()
    return render_template('ai_calendar.html', assignments=assignments, enumerate=enumerate)


@ai_calendar_bp.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    subject_form = SubjectForm()
    subjects = current_user.subjects
    if subject_form.validate_on_submit():
        subject_name = subject_form.subject.data
        new_subject = Subject(user_id=current_user.id, subject=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully.', 'success')
        return redirect(url_for('ai_calendar.configure'))
    freetime_form = FreetimeForm()
    freetime = current_user.freetime
    if freetime_form.validate_on_submit():
        freetime_name = freetime_form.freetime.data
        new_freetime = Freetime(user_id=current_user.id, freetime=freetime_name)
        db.session.add(new_freetime)
        db.session.commit()
        flash('Freetime added successfully.', 'success')
        return redirect(url_for('ai_calendar.configure'))
    return render_template('config_calendar.html', subject_form=subject_form, subjects=subjects, freetime_form=freetime_form, freetime=freetime, enumerate=enumerate)

@ai_calendar_bp.route('/remove_subject/<int:subject_id>', methods=['POST'])
@login_required
def remove_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id == current_user.id:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject removed successfully.', 'success')
    else:
        flash('Unauthorized to remove this subject.', 'error')
    return redirect(url_for('ai_calendar.configure'))

@ai_calendar_bp.route('/remove_freetime/<int:freetime_id>', methods=['POST'])
@login_required
def remove_freetime(freetime_id):
    freetime = Freetime.query.get_or_404(freetime_id)
    if freetime.user_id == current_user.id:
        db.session.delete(freetime)
        db.session.commit()
        flash('Freetime removed successfully.', 'success')
    else:
        flash('Unauthorized to remove this freetime.', 'error')
    return redirect(url_for('ai_calendar.configure'))

@ai_calendar_bp.route('/generate_tasks')
def generate_tasks():
    user = User.query.get(current_user.id)
    if user.last_generated != date.today():
        user.tokens_earned_today = 0
        db.session.commit()
    if current_user.freetime:
        if current_user.last_generated != date.today():
            Assignments.query.filter_by(user_id = current_user.id).delete()
            user_freetimes = current_user.freetime
            time_slots = [freetime.freetime for freetime in user_freetimes]
            user_subjects = current_user.subjects
            subjects_list = [subject.subject for subject in user_subjects]
            time_slots_len = len(time_slots)
            optimizer = current_user.optimizer
            slots_to_select = math.floor((time_slots_len * optimizer) / 10)
            if slots_to_select == 0:
                slots_to_select = 1
            selected_slots = random.sample(time_slots, slots_to_select)
            assignments = {}
            num_subjects = len(subjects_list)
            for i, slot in enumerate(selected_slots):
                subject_index = i % num_subjects
                subject = subjects_list[subject_index]
                assignments[slot] = subject
            for time_slot, subject in assignments.items():
                assignment = Assignments(user=current_user, time_slot=time_slot, subject=subject)
                db.session.add(assignment)
            current_user.last_generated = date.today()
            db.session.commit()
        
    return redirect(url_for('ai_calendar.ai_calendar'))

@ai_calendar_bp.route('/remove_all_entries')
def remove_all_entries():
    Subject.query.filter_by(user_id=current_user.id).delete()
    Freetime.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('ai_calendar.configure'))

@ai_calendar_bp.route('/task_completed', methods=['POST'])
def task_completed():
    time_slot = request.form.get('time_slot')
    assignment = Assignments.query.filter_by(user_id=current_user.id, time_slot=time_slot).first()
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        user = User.query.get(current_user.id)
        if current_user.tokens_earned_today < 7:
            user.pro_token += 1
            user.tokens_earned_today += 1
            db.session.commit()
    return redirect(url_for('ai_calendar.ai_calendar'))

@ai_calendar_bp.route('/remove_all_tasks')
def remove_all_tasks():
    Assignments.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('ai_calendar.ai_calendar'))