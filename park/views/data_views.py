from flask import Blueprint, request, render_template
from park.models import ParkData
from .. import db

bp = Blueprint('data', __name__, url_prefix='/data')

@bp.route('/', methods=['GET'])
def check_data():
    parkdata_list = ParkData.query.order_by(ParkData.time.asc())
    
    """
    park_data = ParkData.query.all()
    result = [
        {
            "id": data.id,
            "time": data.time,
            "event": data.event,
            "type": data.type
        } for data in park_data
    ]
    return jsonify(result)
    """
    
    return render_template('data_show.html', data_list=parkdata_list)

@bp.route('/', methods=['POST'])
def add_park_data():
    new_data = request.get_json()
    park_data = ParkData(
        time=new_data['time'],
        event=new_data['event'],
        type=new_data['type']
    )
    db.session.add(park_data)
    db.session.commit()
    return jsonify({"message": "Park data added successfully!"}), 201