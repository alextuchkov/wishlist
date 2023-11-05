from flask import render_template, request, flash, url_for, redirect, jsonify

from models import User, List, ListItem
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user,
    login_manager,
)
from datetime import datetime
from app import app, session, login_manager, db


@app.route("/")
def index():
    return render_template("index.html")


@login_manager.user_loader
def user_loader(user_id):
    # return User.query.get(user_id)
    with app.app_context():
        return session.get(User, user_id)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        generated_password_hash = generate_password_hash(request.form.get("password"))
        new_user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password_hash=generated_password_hash,
            active=True,
        )
        session.add(new_user)
        session.commit()
        session.close()
        return redirect(url_for("signin"))
    return render_template("auth.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if a valid user with the provided email exists
        user = session.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            user.authenticated = True
            db.session.commit()  # Use db.session to commit changes
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login credentials", "error")

    # Render the login template for both GET and unsuccessful POST requests
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        try:
            new_list_name = request.form.get("list_name")
            new_list_descrp = request.form.get("list_description")
            deadline = datetime.strptime(
                request.form.get("deadline"), "%Y-%m-%d"
            ).date()

            new_list = List(
                name=new_list_name,
                description=new_list_descrp,
                deadline=deadline,
                owner=current_user.id,
            )

            session.add(new_list)
            session.commit()
            session.close()
            newly_created_list = (
                session.query(List).filter_by(name=new_list_name).first()
            )
            return redirect(url_for("edit", id=newly_created_list.id))

        except Exception as e:
            flash(f"An error occurred while adding list item: {str(e)}", "error")
            return "Some Error"

    return render_template("create.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    page_title = "Edit list"
    list = session.query(List).filter_by(id=id).first()
    list_items = session.query(ListItem).filter_by(list=list.id).all()

    if request.method == "POST":
        deadline_date = datetime.strptime(
            request.form.get("deadline"), "%Y-%m-%d"
        ).date()

        list.name = request.form.get("name")
        list.description = request.form.get("description")
        list.deadline = deadline_date

        try:
            session.commit()
            flash("List details updated successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while updating list details: {str(e)}", "error")

        return redirect(url_for("edit", id=list.id))

    return render_template(
        "edit.html", list=list, list_items=list_items, title=page_title
    )


@app.route("/add_list_item", methods=["GET", "POST"])
@login_required
def add_list_item():
    if request.method == "POST":
        item_name = request.form.get("item-name")
        item_description = request.form.get("item-description")
        item_price = request.form.get("item-price")
        item_url = request.form.get("item-link")
        ref_id = request.form.get("ref-id")

        new_list_item = ListItem(
            item_name=item_name,
            item_description=item_description,
            price=item_price,
            url=item_url,
            list=ref_id,
        )
        try:
            session.add(new_list_item)
            session.commit()
            flash("List Item added successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while adding list item: {str(e)}", "error")

        return redirect(url_for("edit", id=ref_id))


@app.route("/update_list_item", methods=["GET", "POST"])
@login_required
def update_list_item():
    if request.method == "POST":
        item_id = request.form.get("item-id")
        item_name = request.form.get("item-name")
        item_description = request.form.get("item-description")
        item_price = request.form.get("item-price")
        item_url = request.form.get("item-link")
        ref_id = request.form.get("ref-id")

        list_item = session.query(ListItem).filter_by(id=item_id).first()

        if list_item is not None:
            list_item.item_name = item_name
            list_item.item_description = item_description
            list_item.price = item_price
            list_item.url = item_url

        try:
            session.commit()
            flash("List Item updated successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while updating list item: {str(e)}", "error")

        return redirect(url_for("edit", id=ref_id))


@app.route("/delete_list_item/<int:id>", methods=["GET", "POST"])
@login_required
def delete_list_item(id):
    list_item = session.query(ListItem).filter_by(id=id).first()
    if list_item:
        try:
            session.delete(list_item)
            session.commit()
            flash("List item deleted successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while deleting the list item: {str(e)}", "error")
    else:
        flash("List item not found.", "error")

    return redirect(url_for("edit", id=list_item.list))


@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    list = session.query(List).filter_by(id=id).first()
    if list:
        try:
            session.delete(list)
            session.commit()
            flash("List item deleted successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while deleting the list item: {str(e)}", "error")
    else:
        flash("List item not found.", "error")

    return redirect(url_for("dashboard"))


@app.route("/list/<int:id>")
def list(id):
    list = session.query(List).filter_by(id=id).first()
    list_items = session.query(ListItem).filter_by(list=list.id).all()

    return render_template("list.html", list=list, list_items=list_items)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Opens dashboard page for logged in user"""
    lists = session.query(List).filter_by(owner=current_user.id).all()
    if request.method == "POST":
        user = session.query(User).filter_by(id=current_user.id).first()
        if user:
            user.username = request.form.get("username")
            user.email = request.form.get("email")
            user.about_me = request.form.get("about-me")

            try:
                session.commit()
                flash("User details updated successfully.", "success")
            except Exception as e:
                session.rollback()
                flash(
                    f"An error occurred while updating user details: {str(e)}", "error"
                )
        else:
            flash("User not found.", "error")

        return redirect(url_for("dashboard"))

    return render_template("dashboard.html", lists=lists)
