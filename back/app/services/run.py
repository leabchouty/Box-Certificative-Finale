from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from algorithmewithdb import run_grouping_algorithm

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/api/generate-groups', methods=['POST'])
def generate_groups():
    try:
        data = request.get_json()
        
        # Extract parameters from request
        students = data.get('students', [])
        preferences = data.get('preferences', {})
        n = data.get('n', 4)
        
        if not students:
            return jsonify({'error': 'No students provided'}), 400
        
        if len(students) < n:
            return jsonify({'error': f'Not enough students ({len(students)}) to form groups of size {n}'}), 400
        
        # Run the algorithm
        result = run_grouping_algorithm(students, preferences, n)
        
        if result['success']:
            return jsonify({
                'success': True,
                'groups': result['groups'],
                'satisfaction_score': result['satisfaction_score'],
                'total_students': result['total_students'],
                'num_groups': result['num_groups']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
