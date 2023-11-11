from flask import render_template, request, flash, url_for, redirect, jsonify

from sqlalchemy.orm import joinedload
from sqlalchemy import or_


from models import User, List, ListItem, Comment, FollowedLists
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user,
    login_manager,
)
from datetime import datetime
from app import app, session, login_manager
from validations import is_valid_email, is_valid_password


@app.route("/")
def index():
    return render_template("index.html")


@login_manager.user_loader
def user_loader(user_id):
    with app.app_context():
        return session.get(User, user_id)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if is_valid_email(email) == False:
            flash("Not a valid email")
        # TODO Switch On password validation
        # elif is_valid_password(password) == False:
        #     flash("Password is less than 6 characters")
        else:
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                flash("Email is already in use", "error")
            else:
                try:
                    new_user = User(
                        username=username,
                        email=email,
                        password_hash=generate_password_hash(password),
                        active=True,
                    )
                    session.add(new_user)
                    session.commit()
                    return redirect(url_for("signin"))
                except Exception as e:
                    flash("An error occurred while signing up", "error")
    title = "Створити профіль"
    return render_template("signup.html", title=title)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if a valid user with the provided email exists
        user = session.query(User).filter_by(email=email).first()
        if is_valid_email(email) == False:
            flash("Not a valid email", "error")
        # TODO Switch On password validation
        # elif is_valid_password(password) == False:
        #     flash("Password is not secure")

        elif user and check_password_hash(user.password_hash, password):
            user.authenticated = True
            session.commit()
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login credentials", "error")
    title = "Створити профіль"
    return render_template("signin.html", title=title)


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

    return render_template(
        "edit.html", list=list, list_items=list_items, title=page_title
    )


@app.route("/edit_list", methods=["POST"])
@login_required
def edit_list():
    if request.method == "POST":
        list_id = request.form.get("list-id")
        list_name = request.form.get("name")
        list_description = request.form.get("description")
        deadline_date = datetime.strptime(
            request.form.get("deadline"), "%Y-%m-%d"
        ).date()

        list = session.query(List).filter_by(id=list_id).first()

        if list is not None:
            list.name = list_name
            list.description = list_description
            list.deadline = deadline_date

        try:
            session.commit()
            flash("List updated successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while updating List: {str(e)}", "error")

        return redirect(url_for("edit", id=list_id))


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
    page_title = f"{list.name}"
    list_items = session.query(ListItem).filter_by(list=list.id).all()
    try:
        followed_list_references = (
            session.query(FollowedLists).filter_by(follower=current_user.id).all()
        )

        # join
        followed_lists = [
            session.query(List).filter_by(id=followed_list.list).first()
            for followed_list in followed_list_references
        ]

        return render_template(
            "list.html",
            list=list,
            list_items=list_items,
            title=page_title,
            followed_lists=followed_lists,
        )
    except Exception as e:
        pass

    return render_template(
        "list.html",
        list=list,
        list_items=list_items,
        title=page_title,
    )


@app.route("/book", methods=["POST"])
@login_required
def book():
    try:
        data = request.get_json()

        item_id = data.get("item-id")
        ref_id = data.get("ref-id")

        list_item = session.query(ListItem).filter_by(id=item_id).first()

        if list_item is not None:
            if list_item.is_booked and list_item.booked_by == current_user.id:
                # If the item is already booked by the current user, unbook it and clear sharer information
                list_item.is_booked = False
                list_item.booked_by = None
                list_item.sharer_1 = None
                list_item.sharer_2 = None
                flash("You unbooked item!", "success")
            else:
                # Otherwise, book the item and clear sharer information
                list_item.is_booked = True
                list_item.booked_by = current_user.id
                list_item.sharer_1 = None
                list_item.sharer_2 = None
                flash("You booked item!", "success")

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while processing the request: {str(e)}", "error")

        return jsonify({"redirect_url": url_for("list", id=ref_id)})
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/split", methods=["POST"])
@login_required
def split():
    try:
        data = request.get_json()

        item_id = data.get("item-id")
        ref_id = data.get("ref-id")

        list_item = session.query(ListItem).filter_by(id=item_id).first()

        if list_item is not None:
            # Check if the current user is already a sharer
            if current_user.id in {list_item.sharer_1, list_item.sharer_2}:
                # If yes, remove them
                if list_item.sharer_1 == current_user.id:
                    list_item.sharer_1 = None
                elif list_item.sharer_2 == current_user.id:
                    list_item.sharer_2 = None
                flash("Ви відмінили розділення цього подарунка", "success")
            else:
                # If not, add them as a sharer
                if list_item.sharer_1 is None:
                    list_item.sharer_1 = current_user.id
                elif list_item.sharer_2 is None:
                    list_item.sharer_2 = current_user.id
                else:
                    flash(
                        "Тільки 2 користувачі можуть розділити цей подарунок", "error"
                    )
            # list_item.is_shared = True

        try:
            session.commit()
            flash(
                "Успіх!",
                "success",
            )
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while splitting item: {str(e)}", "error")

        return jsonify({"redirect_url": url_for("list", id=ref_id)})

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/toggle_follow", methods=["POST"])
@login_required
def toggle_follow():
    list_id = request.form.get("list_id")
    user_id = current_user.id

    # Check if the user is already following the list
    followed_list = (
        session.query(FollowedLists).filter_by(list=list_id, follower=user_id).first()
    )

    if followed_list:
        # If the user is following the list, unfollow it
        session.delete(followed_list)
        session.commit()
        flash("Ви відписалися від списку.", "success")
    else:
        # If the user is not following the list, follow it
        new_followed = FollowedLists(list=list_id, follower=user_id)
        session.add(new_followed)
        session.commit()
        flash("Ви слідкуєте за списком.", "success")

    return redirect(url_for("list", id=list_id))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    lists = session.query(List).filter_by(owner=current_user.id).all()

    followed_list_references = (
        session.query(FollowedLists).filter_by(follower=current_user.id).all()
    )

    followed_lists = [
        session.query(List).filter_by(id=followed_list.list).first()
        for followed_list in followed_list_references
    ]

    booked_items = session.query(ListItem).filter_by(booked_by=current_user.id).all()

    shared_items = (
        session.query(ListItem)
        .filter(
            or_(
                ListItem.sharer_1 == current_user.id,
                ListItem.sharer_2 == current_user.id,
            )
        )
        .all()
    )

    title = "Профіль"
    return render_template(
        "dashboard.html",
        lists=lists,
        followed_lists=followed_lists,
        title=title,
        booked_items=booked_items,
        shared_items=shared_items,
    )


@app.route("/edit_dashboard", methods=["POST"])
@login_required
def edit_dashboard():
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
            flash(f"An error occurred while updating user details: {str(e)}", "error")
    else:
        flash("User not found.", "error")

    return redirect(url_for("dashboard"))


@app.route("/listitem/<int:id>")
def listitem(id):
    comments = session.query(Comment).filter_by(list_item=id).all()
    list_item = session.query(ListItem).filter_by(id=id).first()
    page_title = list_item.item_name

    return render_template(
        "listitem.html", comments=comments, title=page_title, list_item=list_item
    )


@app.route("/comment/<int:id>", methods=["POST"])
@login_required
def comment(id):
    if request.method == "POST":
        new_comment = Comment(
            comment=request.form.get("comment"),
            author_id=current_user.id,
            list_item=id,
        )
        try:
            session.add(new_comment)
            session.commit()
            flash("Ви залиши комментар.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while adding list item: {str(e)}", "error")

        return redirect(url_for("comments", id=id))
