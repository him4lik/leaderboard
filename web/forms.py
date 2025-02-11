from django.forms import ModelForm, TextInput
from backend.models import Contestant, Game, GameSession


class ContestantForm(ModelForm):
    class Meta:
        model = Contestant
        fields = ["username", "gender", "score"]
        widgets = {
            'score': TextInput(attrs={'disabled': 'disabled'}),
        }

class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ["name", "active"]
        # widgets = {
        #     'score': TextInput(attrs={'disabled': 'disabled'}),
        # }

class ContestantUpdateForm(ModelForm):
    class Meta:
        model = Contestant
        fields = ["username", "gender", "score"]
        widgets = {
            # 'score': TextInput(attrs={'disabled': 'disabled'}),
            # 'username': TextInput(attrs={'disabled': 'disabled'}),
            'username': TextInput(attrs={'readonly': 'readonly'}),
            'score': TextInput(attrs={'readonly': 'readonly'}),
        }
        
class GameUpdateForm(ModelForm):
    class Meta:
        model = Game
        fields = ["name", "active", "description"]
        widgets = {
            # 'score': TextInput(attrs={'disabled': 'disabled'}),
            # 'username': TextInput(attrs={'disabled': 'disabled'}),
            'name': TextInput(attrs={'readonly': 'readonly'}),
        }
        
class GameSessionForm(ModelForm):
    class Meta:
        model = GameSession
        fields = ["contestants"]
        # widgets = {
        #     'duration_in_sec': TextInput(attrs={'disabled': 'disabled'}),
        #     'game': TextInput(attrs={'readonly': 'readonly'}),
        #     'active': TextInput(attrs={'readonly': 'readonly'}),
        # }