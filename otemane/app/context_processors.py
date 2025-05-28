def selected_child(request):
    return {
        'selected_child_id': request.session.get('selected_child_id'),
        'selected_child': request.session.get('selected_child'),
    }