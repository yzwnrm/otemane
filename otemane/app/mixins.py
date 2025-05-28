from django.shortcuts import redirect

class RequireChildSelectedMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('selected_child_id') or request.session['selected_child_id'] == 'all':
            return redirect('app:home')  # または子ども選択ビューへ
        return super().dispatch(request, *args, **kwargs)