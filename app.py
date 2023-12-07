from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

# Route for displaying the list of plants
@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

# Route for the 'About' page
@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

# Route for creating new plants
@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('plant_name')
        variety = request.form.get('variety')
        photo_url = request.form.get('photo_url')
        date_planted = request.form.get('date_planted')
        
        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo_url,
            'date_planted': date_planted
        }
        
        # Insert new plant into the database
        created_plant = mongo.db.plants.insert_one(new_plant)
        plant_id = created_plant.inserted_id

        return redirect(url_for('detail', plant_id=plant_id))

    # Otherwise, it's a GET request and we just want to render the template
    return render_template('create.html')

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error handler."""
    return render_template('404.html'), 404

# Route for displaying plant details
@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    if not plant_to_show:
        # If plant not found, return custom 404 page
        abort(404)
    
    harvests = mongo.db.harvests.find({'plant_id': plant_id})
    harvest_array = list(harvests)
    context = {
        'plant': plant_to_show,
        'harvests': harvest_array
    }
    return render_template('detail.html', **context)

# Route for handling harvest data
@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    new_harvest = {
        'quantity': request.form.get('harvested_amount'), # e.g. '3 tomatoes'
        'date_harvested': request.form.get('date_harvested'),
        'plant_id': plant_id
    }

    created_harvest = mongo.db.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=plant_id))

# Route for editing plant details
@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
         # Update plant details in the database
        plant_to_update = mongo.db.plants.update_one({'_id': ObjectId(plant_id)}, {'$set': {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo_url'),
            'date_planted': request.form.get('date_planted')
        }})
        return redirect(url_for('detail', plant_id=plant_id))
    
    # Retrieve plant details and render the edit template
    else:
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }
        return render_template('edit.html', **context)

# Route for deleting plants
@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """Deletes one plant or all plants with the same planet_id."""
    plant_to_delete = mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})
    plants_to_delete = mongo.db.harvests.delete_many({'_id': ObjectId(plant_id)})
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)