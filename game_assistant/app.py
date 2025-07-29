from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from game_assistant.models import Instance, Village
from game_assistant.optimal import solve_instance
from game_assistant.forms import VillageForm, RouteForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'keyofgod'  # Replace with a secure key in production

instance = Instance().load_instance_from_file('instance.json')
optimal_routes = {}

@app.route('/')
def index():
    villages = instance.villages
    villages_js = [
        {
            "name": v.name,
            "production": v.production,
            "routes": [{"target": target, "amount": amount} for target, amount in v.routes.items()] if v.routes else []
        }
        for v in villages
    ]
    list_transposed = instance.routes_matrix.transpose().tolist() if instance.routes_matrix is not None else []
    return render_template("index.html",
                            villages=villages,
                            villages_js=villages_js,
                            list_transposed=list_transposed,
                            mapping=instance.villages_map,
                            optimal_routes=optimal_routes)


@app.route('/add_village', methods=['GET','POST'])
def add_village():
    form = VillageForm()
    if form.validate_on_submit():
        name = form.name.data
        production = form.production.data
        if instance.get_village(name):
            flash(f"Village '{name}' already exists.", 'error')
        else:
            village = Village(name=name, production=production)
            instance.add_village(village)
            flash(f"Village '{name}' added successfully.", 'success')
            return redirect(url_for('index'))
    return render_template('add_village.html', form=form)

@app.route('/edit_village/<string:name>', methods=['GET', 'POST'])
def edit_village(name):
    village = instance.get_village(name)
    if not village:
        flash(f"Village '{name}' does not exist.", 'error')
    form = VillageForm(obj=village)
    if form.validate_on_submit():
        village.name = form.name.data
        village.production = form.production.data
        flash(f"Village '{name}' updated successfully.", 'success')
        return redirect(url_for('index'))
    return render_template('edit_village.html', form=form, village=village)

@app.route('/remove_village/<string:name>')
def remove_village(name):
    try:
        instance.remove_village(name)
        flash(f"Village '{name}' removed successfully.", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('index'))

@app.route('/solve_instance', methods=['GET'], endpoint='solve_instance_route')
def solve_instance_route():
    try:
        solution = solve_instance(instance)
        optimal_routes.clear()
        optimal_routes.update(solution)
        flash("Instance solved successfully.", 'success')
        return redirect(url_for('index'))
    except ValueError as e:
        flash(str(e), 'error')


@app.route('/add_route', methods=['GET', 'POST'])
def add_route():
    form = RouteForm()
    form.from_village.choices = [(v.name, v.name) for v in instance.villages]
    form.to_village.choices = [(v.name, v.name) for v in instance.villages]
    if not form.from_village.choices or not form.to_village.choices:
        flash("No villages available to add routes.", 'error')
        return redirect(url_for('index'))
    form.from_village.default = form.from_village.choices[0][0] if form.from_village.choices else ''
    form.to_village.default = form.to_village.choices[0][0] if form.to_village.choices else ''

    if form.validate_on_submit():
        from_village = form.from_village.data
        to_village = form.to_village.data
        amount = form.amount.data
        try:
            instance.add_route(from_village, to_village, amount)
            flash(f"Route from '{from_village}' to '{to_village}' added successfully.", 'success')
        except ValueError as e:
            flash(str(e), 'error')
        return redirect(url_for('index'))
    return render_template('add_route.html', form=form, villages=instance.villages)

@app.route('/edit_route/<string:from_village>/<string:to_village>', methods=['GET', 'POST'])
def edit_route(from_village, to_village):
    village = instance.get_village(from_village)
    if not village or to_village not in village.routes:
        flash(f"Route from '{from_village}' to '{to_village}' does not exist.", 'error')
        return redirect(url_for('index'))
    
    form = RouteForm(obj={'from_village': from_village, 'to_village': to_village, 'amount': village.routes[to_village]})
    if form.validate_on_submit():
        try:
            instance.update_route(from_village, to_village, form.amount.data)
            flash(f"Route from '{from_village}' to '{to_village}' updated successfully.", 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('edit_route.html', form=form, from_village=from_village, to_village=to_village)

@app.route('/remove_route/<string:from_village>/<string:to_village>', methods=['POST'])
def remove_route(from_village, to_village):
    try:
        instance.remove_route(from_village, to_village)
        flash(f"Route from '{from_village}' to '{to_village}' removed successfully.", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

