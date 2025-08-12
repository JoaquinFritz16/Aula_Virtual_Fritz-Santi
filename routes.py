from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import User, Course, Student, Content, Evaluation, Question, Answer
from forms import LoginForm, RegistrationForm, CourseForm, ContentForm, EvaluationForm, QuestionForm, AnswerForm
from flask_login import login_required, current_user

@app.route('/course/<int:course_id>/content/new', methods=['GET', 'POST'])
@login_required
def new_content(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('No tienes permiso para agregar contenido a este curso.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    form = ContentForm()
    if form.validate_on_submit():
        content = Content(title=form.title.data, description=form.description.data, file_path=form.file_path.data, course_id=course_id)
        db.session.add(content)
        db.session.commit()
        flash('Contenido agregado exitosamente.', 'success')
        return redirect(url_for('course_detail', course_id=course_id))

    return render_template('new_content.html', form=form, course=course)

@app.route('/course/<int:course_id>/evaluation/new', methods=['GET', 'POST'])
@login_required
def new_evaluation(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('No tienes permiso para agregar evaluaciones a este curso.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    form = EvaluationForm()
    if form.validate_on_submit():
        evaluation = Evaluation(title=form.title.data, description=form.description.data, course_id=course_id)
        db.session.add(evaluation)
        db.session.commit()
        flash('Evaluación agregada exitosamente.', 'success')
        return redirect(url_for('course_detail', course_id=course_id))

    return render_template('new_evaluation.html', form=form, course=course)

@app.route('/evaluation/<int:evaluation_id>/question/new', methods=['GET', 'POST'])
@login_required
def new_question(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    if evaluation.course.instructor_id != current_user.id:
        flash('No tienes permiso para agregar preguntas a esta evaluación.', 'danger')
        return redirect(url_for('course_detail', course_id=evaluation.course_id))

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(text=form.text.data, evaluation_id=evaluation_id)
        db.session.add(question)
        db.session.commit()
        flash('Pregunta agregada exitosamente.', 'success')
        return redirect(url_for('evaluation_detail', evaluation_id=evaluation_id))

    return render_template('new_question.html', form=form, evaluation=evaluation)

@app.route('/question/<int:question_id>/answer/new', methods=['GET', 'POST'])
@login_required
def new_answer(question_id):
    question = Question.query.get_or_404(question_id)
    if question.evaluation.course.instructor_id != current_user.id:
        flash('No tienes permiso para agregar respuestas a esta pregunta.', 'danger')
        return redirect(url_for('evaluation_detail', evaluation_id=question.evaluation_id))

    form = AnswerForm()
    if form.validate_on_submit():
        answer = Answer(text=form.text.data, is_correct=form.is_correct.data, question_id=question_id)
        db.session.add(answer)
        db.session.commit()
        flash('Respuesta agregada exitosamente.', 'success')
        return redirect(url_for('evaluation_detail', evaluation_id=question.evaluation_id))

    return render_template('new_answer.html', form=form, question=question)
