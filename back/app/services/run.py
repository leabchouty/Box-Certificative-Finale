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

if name == 'main':
    app.run(debug=True, host='0.0.0.0', port=5000)