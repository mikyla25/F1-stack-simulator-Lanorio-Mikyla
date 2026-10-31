
from flask import Flask, render_template, request, redirect, url_for, session, flash
from queue_model import Queue

app = Flask(__name__)
app.secret_key = "queue_simulator_secret_key"

@app.route('/')
def index():
    raw_items = session.get('queue_items', [])
    q = Queue()
    q.items = raw_items

    highlight_front = request.args.get('peek', 'false').lower() == 'true'

    return render_template(
        'index.html',
        items=q.items,
        size=q.size(),
        front_item=q.peek() if not q.is_empty() else None,
        highlight=highlight_front,
        removed_items=session.get('removed_items', [])
    )

@app.route('/operate', methods=['POST'])
def operate():
    action = request.form.get('action')
    value = request.form.get('value', '').strip()

    q = Queue()
    q.items = session.get('queue_items', [])

    removed_items = session.get('removed_items', [])
    highlight_front = False

    if action == 'enqueue':
        if not value:
            flash("Please enter a value.", "error")
        elif len(value) > 24:
            flash("Maximum 24 characters allowed.", "error")
        elif q.size() >= 20:
            flash("Queue limit of 20 items reached.", "error")
        else:
            q.enqueue(value)
            flash(f"Enqueued: {value}", "success")

    elif action == 'dequeue':
        if q.is_empty():
            flash("Cannot dequeue. Queue is empty.", "error")
        else:
            removed = q.dequeue()
            removed_items.append(removed)
            flash(f"Dequeued: {removed}", "success")

    elif action == 'peek':
        if q.is_empty():
            flash("Cannot peek. Queue is empty.", "error")
        else:
            highlight_front = True
            flash(f"Front item: {q.peek()}", "success")

    elif action == 'clear':
        q.clear()
        removed_items = []
        flash("Queue and removed items cleared.", "success")

    else:
        flash("Unknown operation.", "error")

    session['queue_items'] = q.items
    session['removed_items'] = removed_items

    if highlight_front:
        return redirect(url_for('index', peek='true'))

    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
