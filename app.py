import datetime
import os
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/medical'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/pharm")
def get_pharmacies():
    pharmacies = Pharmacy.query.all()
    return render_template('pharma.html', data= pharmacies)

@app.route("/pharm/<int:pharmacy_id>", methods=["POST", "DELETE"])
def delete_pharmacy(pharmacy_id):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    db.session.delete(pharmacy)
    db.session.commit()
    return redirect(url_for('get_pharmacies'))


@app.route("/pharm/add", methods=["GET", "POST"])
def add_pharmacy():
    if request.method == "GET":
        return render_template("add.html")
        
    if request.method == "POST":
        try:
            name = request.form.get("name")
            description = request.form.get("description")
            
            if not name or not description:
                flash("Name and description are required", "error")
                return render_template("add.html")
            
            new_pharmacy = Pharmacy(
                name=name,
                description=description
            )
            
            db.session.add(new_pharmacy)
            db.session.commit()
            
            flash("Pharmacy added successfully!", "success")
            return redirect(url_for("get_pharmacies"))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Database error occurred", "error")
            return render_template("add.html")
            
        except Exception as e:
            db.session.rollback()
            flash("An unexpected error occurred", "error")
            return render_template("add.html")


@app.route("/pharm/<int:pharmacy_id>/edit", methods=["GET"])
def edit_pharmacy(pharmacy_id):
    try:
        pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
        return render_template("edit.html", pharmacy=pharmacy)
    except SQLAlchemyError as e:
        flash("Error accessing pharmacy details", "error")
        return redirect(url_for("get_pharmacies"))

@app.route("/pharm/<int:pharmacy_id>/update", methods=["POST"])
def update_pharmacy(pharmacy_id):
    try:
        pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
        
        name = request.form.get("name")
        description = request.form.get("description")
        
        if not name or not description:
            flash("Name and description are required", "error")
            return redirect(url_for("edit_pharmacy", pharmacy_id=pharmacy_id))
        
        pharmacy.name = name
        pharmacy.description = description
        
        db.session.commit()
        flash("Pharmacy updated successfully!", "success")
        return redirect(url_for("get_pharmacies"))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Database error occurred", "error")
        return redirect(url_for("edit_pharmacy", pharmacy_id=pharmacy_id))
        
    except Exception as e:
        db.session.rollback()
        flash("An unexpected error occurred", "error")
        return redirect(url_for("edit_pharmacy", pharmacy_id=pharmacy_id))
        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)