from flask import Flask, render_template, redirect, url_for, flash, current_app, jsonify
import argparse

from game_assistant.models import Instance, Village
from game_assistant.optimal import solve_instance
from game_assistant.forms import VillageForm, RouteForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'keyofgod'  # Replace with a secure key in production

@app.route('/')
def index():
    instance = current_app.config['INSTANCE']
    optimal_routes = current_app.config.get('OPTIMAL_ROUTES', {})
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
    instance = current_app.config['INSTANCE']
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
    current_app.config['INSTANCE'] = instance
    return render_template('add_village.html', form=form)

@app.route('/edit_village/<string:name>', methods=['GET', 'POST'])
def edit_village(name):
    instance = current_app.config['INSTANCE']
    village = instance.get_village(name)
    if not village:
        flash(f"Village '{name}' does not exist.", 'error')
    form = VillageForm(obj=village)
    if form.validate_on_submit():
        village.name = form.name.data
        village.production = form.production.data
        flash(f"Village '{name}' updated successfully.", 'success')
        return redirect(url_for('index'))
    current_app.config['INSTANCE'] = instance
    return render_template('edit_village.html', form=form, village=village)

@app.route('/remove_village/<string:name>')
def remove_village(name):
    instance = current_app.config['INSTANCE']
    try:
        instance.remove_village(name)
        current_app.config['INSTANCE'] = instance
        flash(f"Village '{name}' removed successfully.", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('index'))

@app.route('/solve_instance', methods=['GET'], endpoint='solve_instance_route')
def solve_instance_route():
    instance = current_app.config['INSTANCE']
    optimal_routes = current_app.config.get('OPTIMAL_ROUTES', {})
    try:
        solution = solve_instance(instance)
        optimal_routes.clear()
        optimal_routes.update(solution)
        current_app.config['OPTIMAL_ROUTES'] = optimal_routes
        flash("Instance solved successfully.", 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(str(e), 'error')
        optimal_routes.clear()
        return redirect(url_for('index'))


@app.route('/add_route', methods=['GET', 'POST'])
def add_route():
    instance = current_app.config['INSTANCE']
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
        current_app.config['INSTANCE'] = instance
        return redirect(url_for('index'))
    return render_template('add_route.html', form=form, villages=instance.villages)

@app.route('/edit_route/<string:from_village>/<string:to_village>', methods=['GET', 'POST'])
def edit_route(from_village, to_village):
    instance = current_app.config['INSTANCE']
    village = instance.get_village(from_village)
    if not village or to_village not in village.routes:
        flash(f"Route from '{from_village}' to '{to_village}' does not exist.", 'error')
        return redirect(url_for('index'))
    
    form = RouteForm(obj={'from_village': from_village, 'to_village': to_village, 'amount': village.routes[to_village]})
    if form.validate_on_submit():
        try:
            instance.update_route(from_village, to_village, form.amount.data)
            flash(f"Route from '{from_village}' to '{to_village}' updated successfully.", 'success')
            current_app.config['INSTANCE'] = instance
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('edit_route.html', form=form, from_village=from_village, to_village=to_village)

@app.route('/remove_route/<string:from_village>/<string:to_village>', methods=['POST'])
def remove_route(from_village, to_village):
    instance = current_app.config['INSTANCE']
    try:
        instance.remove_route(from_village, to_village)
        flash(f"Route from '{from_village}' to '{to_village}' removed successfully.", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    current_app.config['INSTANCE'] = instance
    return redirect(url_for('index'))

@app.route("/solution.json")
def solution_json():
    result = app.config.get("OPTIMAL_ROUTES")
    instance = app.config.get("INSTANCE")
    if not result or not instance:
        return jsonify({"error": "No solution found"})

    nodes = []
    name_to_balance = {}
    for v in instance.villages:
        incoming = sum(result.get(src, {}).get(v.name, 0) for src in result)
        outgoing = sum(result.get(v.name, {}).values())
        balance = v.production + incoming - outgoing
        nodes.append({"id": v.name, "balance": balance})
        name_to_balance[v.name] = balance

    links = []
    for src, dests in result.items():
        for dst, amount in dests.items():
            links.append({"source": src, "target": dst, "amount": amount})

    return jsonify({"nodes": nodes, "links": links})

@app.route('/graph')
def graph():
    return render_template('graph.html')


def main():
    parser = argparse.ArgumentParser(description="Game Assistant")
    parser.add_argument('--instance', type=str, default='instance.json', help='Path to the instance file.')
    args = parser.parse_args()
    try:
        instance = Instance().load_instance_from_file(args.instance)
    except FileNotFoundError:
        print(f"Error: File '{args.instance}' not found, using default instance.")
        instance = Instance()
    except ValueError as e:
        print(f"Error loading instance: {e}, using default instance.")
        instance = Instance()

    app.config['INSTANCE'] = instance
    app.config['OPTIMAL_ROUTES'] = {}
    app.run(debug=True)


if __name__ == '__main__':
    main()
