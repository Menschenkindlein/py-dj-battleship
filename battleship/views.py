from django.views.decorators.csrf import csrf_protect
from battleship.battleship import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader
from django.core.urlresolvers import reverse

games = {}
players = {}
wait_dict = {}

def game_preferences(request):
    template = loader.get_template('battleship/game_preferences.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def game(request):
    the_game = games.get(request.session['game'],None)
    if the_game is None:
        return HttpResponseRedirect(reverse('game_preferences'))
    the_player = players[request.session['player']]
    player1_turn, player1_field, player2_field = the_game.watch(the_player)
    if the_game.winner is None:
        template = loader.get_template('battleship/game.html')
        context = RequestContext(request,
                                 {'player1_field' : player1_field,
                                  'player2_field' : player2_field,
                                  'turn' : player1_turn})
    else:
        template = loader.get_template('battleship/endgame.html')
        context = Context({'player1_field' : player1_field,
                           'player2_field' : player2_field,
                           'you_win' : the_game.winner == the_player})
    return HttpResponse(template.render(context))

def waiting(request):
    if wait_dict.get('game',None) is not None:
        request.session['game'] = wait_dict['game']
        wait_dict['game'] = None
        return HttpResponseRedirect(reverse('game'))
    else:
        template = loader.get_template('battleship/waiting.html')
        context = Context()
    return HttpResponse(template.render(context))

@csrf_protect
def startgame(request):
    request.session['game'] = hash(request.session) * hash(request.session)
    request.session['player'] = hash(request.session)
    ships = request.POST.get('ships', None)
    opponent = request.POST.get('opponent','random')
    if ships == None:
        players[request.session['player']] = Player()
    else:
        players[request.session['player']] = Player(None, ships)
    if opponent == 'systematic':
        opponent = Player(SystematicShooter())
    elif opponent == 'human':
        if wait_dict.get('player',None) is None:
            wait_dict['player'] = players[request.session['player']]
            return HttpResponseRedirect(reverse('waiting'))
        opponent = wait_dict['player']
        wait_dict['player'] = None
        wait_dict['game'] = request.session['game']
    else:
        opponent = Player(RandomShooter())
    games[request.session['game']] = Game(opponent,
                                          players[request.session['player']])
    return HttpResponseRedirect(reverse('game'))

@csrf_protect
def turn(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    games[request.session['game']].turn(players[request.session['player']],x,y)
    return HttpResponseRedirect(reverse('game'))


