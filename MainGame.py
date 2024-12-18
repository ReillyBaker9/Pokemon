from Classes import *
from Pokedex import *
from random import randint
from OpponentAI import *
from Types import *
import copy
import sys


def initializeGame():
    # define the player as a global variable to add a team to
    global Player
    # Player can decide their name and which Pokemon they want on their team
    Player.name = input("What is your name? ")
    Player.team = []
    
    # global pokeList
    # pokeList = [Charizard, Venusaur, Blastoise]
    chooseTeam()
    return

def chooseTeam():
    global pokeList
    pokeList = []
    acceptable_inputs = [1, 2, 3, 4, 5, 6]
    try:
        team_length = int(input("How many Pokemon would you like? (Max of 6)\n"))
    except ValueError:
        team_length = -1
    while team_length not in acceptable_inputs:
        print("Invalid selection")
        try:
            team_length = int(input("How many Pokemon would you like? (Max of 6)\n"))
        except ValueError:
            team_length = -1
    # print out the entire Pokedex for number reference
    for i in range(len(Pokedex)):
        mon = Pokedex[i]
        print(f"{mon.pokedex}. {mon.name}")
    # let them choose their Pokemon
    for i in range(team_length):
        try:
            selection = int(input(f"Which Pokemon do you want? Use the Pokedex # ({i+1} of {team_length})\n")) - 1
        except ValueError:
            selection = -1
        while selection not in range(len(Pokedex)):
            print("Invalid selection")
            try:
                selection = int(input(f"Which Pokemon do you want? Use the Pokedex # ({i+1} of {team_length})\n")) - 1
            except ValueError:
                selection = -1
        print(f"Chose {Pokedex[selection].name}!")
        pokeList.append(Pokedex[selection])
        
def startBattle():
    Player.team = []
    # using the copy module to create copies I can then modify the attributes of
    for guy in pokeList:
        team_member = copy.copy(guy)
        # reset health and stat values in case player is restarting
        team_member.reset_health()
        Player.team.append(team_member)

    # print the team name for reference
    print("Your team consists of:")
    for k in range(len(Player.team)):
        print(Player.team[k].name)
    # define the opponent as a global object like the player
    global opponent 
    opponent = Opponent((input("What is your opponent's name? ")), [])
    # give the opponent Pokemon
    team_size = randint(1, 6)
    while team_size > 0:
        pokeId = randint(0, len(Pokedex) - 1)
        mon = copy.copy(Pokedex[pokeId])
        opponent.team.append(mon)
        team_size -= 1
    # oppList = [Venusaur, Pidgeot, Beedrill]
    # for each in oppList:
    #     opponent.team.append(copy.copy(each))
    # bunch of text to set the stage of the battle
    print("You are challenged by " + opponent.name + "!")
    print(f"{opponent.name}'s team: ")
    for i in range(len(opponent.team)):
        print(opponent.team[i].name)
    # The Pokemon currently in use is an attribute of the user so that they can all be
    # manipulated without passing around a bunch of random objects
    Player.current_pokemon = Player.team[0]
    opponent.current_pokemon = opponent.team[0]
    print("Go! " + Player.current_pokemon.name + "!")
    print(f"{opponent.name} sent out {opponent.current_pokemon.name}!")
    return

def calcPriority(mySpeed, oppSpeed):
    # pretty basic speed calculation. Whoever is faster goes first,
    # and if the speeds are tied, it's a coinflip
    speedTie = randint(1, 2)
    if mySpeed < oppSpeed:
        return 1
    elif mySpeed == oppSpeed:
        return speedTie
    else:
        return 2

def checkAccuracy(move, Player, opponent, user):
        check = randint(1, 100)
        # accuracy check is based on move's accuracy and random int
        # 95% accurate move will miss when check is 96-100
        if check > move.accuracy:
            print(move.name + " missed!")
            return
        # currently status moves don't have an accuracy check, could be changed
        # thinking about changing the ordering of this function in 'Turn'
        # to be less messy
        else:
            if move.moveType == "Status":
                changeStats(move, Player, opponent, user)
                return
            # 1 is the return value tested for a confirmed hit
            else:
                return 1

def calcDamage(move, Attacker, Defender):
        # comes from damage calc page on pokemon wiki, stays same for level 100
        print(f"{Attacker.name}'s {Attacker.current_pokemon.name} used {move.name}!")
        critMult = 1
        # attack reductions and defense boosts are ignored if crit happens
        crit = randint(1, 24)
        if crit == 1:
            critMult = 1.5
            print("Critical hit!")
            # if the effective attacking stat is lower than the base, use the base
            if move.moveType == "Special":
                if Attacker.current_pokemon.spattack > Attacker.current_pokemon.battleSpattack:
                    attacking_stat = Attacker.current_pokemon.spattack
                else:
                    attacking_stat = Attacker.current_pokemon.battleSpattack
            # if the effective defending stat is higher than the base, use the base
                if Defender.current_pokemon.spdefense < Defender.current_pokemon.battleSpdefense:
                    defending_stat = Defender.current_pokemon.spdefense
                else:        
                    defending_stat = Defender.current_pokemon.battleSpdefense
            else:
                if Attacker.current_pokemon.attack > Attacker.current_pokemon.battleAttack:
                    attacking_stat = Attacker.current_pokemon.attack
                else:
                    attacking_stat = Attacker.current_pokemon.battleAttack
                if Defender.current_pokemon.defense < Defender.current_pokemon.battleDefense:
                    defending_stat = Defender.current_pokemon.defense
                else:        
                    defending_stat = Defender.current_pokemon.battleDefense
        # stats used/impacted change depending on the move type
        if move.moveType == "Special":
            attacking_stat = Attacker.current_pokemon.battleSpattack
            defending_stat = Defender.current_pokemon.battleSpdefense
        else:
            attacking_stat = Attacker.current_pokemon.battleAttack
            defending_stat = Defender.current_pokemon.battleDefense
        # based on Pokemon wiki
        level_const = 42
        # all equations are from wiki
        base_damage = ((level_const * move.power * (attacking_stat / defending_stat)) / 50) + 2
        # adding Same Type Attack Bonus if attack type matches user's
        if move.type in Attacker.current_pokemon.type:
            stab_mult = 1.5
        else:
            stab_mult = 1.0
        # all attacks include a random bounded multiplier
        random_factor = (randint(85, 100)) / 100
        # the type multiplier changes based on the effectiveness of the move
        # supereffective moves have higher multipliers, not very effective less
        type_mult = 1.0
        for defender_type in Defender.current_pokemon.type:
            if defender_type in type_effectiveness.get(move.type, {}):
                type_mult *= type_effectiveness[move.type][defender_type]
        # Print effectiveness message, if present
        if type_mult > 1:
            print("It's super effective!")
        elif type_mult < 1:
            print("It's not very effective...")
         
        damage = int(base_damage * stab_mult * random_factor * type_mult * critMult)
        # updating the hp based on the total damage value
        Defender.current_pokemon.battleHp = int(Defender.current_pokemon.battleHp - damage)
        return

def playerSwitch(Player, forced):
    global attackMult, defenseMult, spattackMult, spdefenseMult, speedMult
    # if when the function is called for the player to switch, like their pokemon
    # fainting, and none of their mons have any hp, the battle is over and the 
    # opponent wins
    if all(pokemon.battleHp <= 0 for pokemon in Player.team):
        endBattle(opponent)
    for k in range(len(Player.team)):
        print(str(k + 1) + ". " + Player.team[k].name)
    # if you have a pokemon knocked out, you have to substitute one in,
    # so the back button is not available like it is in the battle menu
    if forced == False:
        print(f"{len(Player.team) + 1}. Back")
    while True:
        try:
            mon = int(input("Which Pokemon will you switch to? ")) - 1
            if not forced and mon == len(Player.team):
                # this is the value that the back button would be
                # so you go back to the Turn menu
                return False
            if mon > len(Player.team) or mon < 0:
                # basic error checking
                print("Invalid input")
                continue
            break
        except ValueError:
            # require a number for input
            print("Invalid input, please enter a number.")
    # can't switch to the current pokemon or one with no hp
    if Player.team[mon] == Player.current_pokemon or Player.team[mon].battleHp <= 0:
        print("Can't switch to that Pokemon!")
        return playerSwitch(Player, forced)
    else:
        # update the current pokemon to the new one selected
        Player.current_pokemon = Player.team[mon]
        print("Switched to " + Player.current_pokemon.name)
        # reset the stat multipliers
        attackMult = defenseMult = spattackMult = spdefenseMult = speedMult = 0
        return True

def changeStats(move, Player, opponent, user):
    global attackMult, defenseMult, spattackMult, spdefenseMult, speedMult
    global oppAttackMult, oppDefenseMult, oppSpattackMult, oppSpdefenseMult, oppSpeedMult
    # most of this function just serves to output the right text
    # for user, 0 is the player, 1 the opponent
    if user == 0:
        userObject = Player
    elif user == 1:
        userObject = opponent
    # create an array of the stats that might be accessed
    statArray = [
        [attackMult, defenseMult, spattackMult, spdefenseMult, speedMult],
        [oppAttackMult, oppDefenseMult, oppSpattackMult, oppSpdefenseMult, oppSpeedMult]
    ]
    # create a name array to correspond with the stat in the move
    statNameArray = ["Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
    # for adding "drastically" for larger stat changes
    punctuation = "."
    changeIntensity = ""
    # decreasing a stat vs increasing, just for text
    if move.modifier < 0:
        change = "decreased"
    else: change = "increased"
    if move.modifier > 1 or move.modifier < -1:
        changeIntensity = " drastically"
        punctuation = "!"
    # this is where the actual number crunching happens
    statArray[user][move.stat] = statArray[user][move.stat] + move.modifier
    # if the stat is going higher than 6, don't allow it
    if statArray[user][move.stat] > 6:
        print(f"{userObject.name}'s {userObject.current_pokemon.name}'s {statNameArray[move.stat]} cannot go any higher")
        statArray[user][move.stat] = 6
    elif statArray[user][move.stat] < -6:
        print(f"{userObject.name}'s {userObject.current_pokemon.name}'s {statNameArray[move.stat]} cannot go any lower")
        statArray[user][move.stat] = -6
    # otherwise, indicate the stat change
    else: 
        print(f"{userObject.name}'s {userObject.current_pokemon.name}'s {statNameArray[move.stat]} {change}{changeIntensity}{punctuation}")
    # update the global variables so the stat changes are applied
    if user == 0:
        attackMult, defenseMult, spattackMult, spdefenseMult, speedMult = statArray[user]
    elif user == 1:
        oppAttackMult, oppDefenseMult, oppSpattackMult, oppSpdefenseMult, oppSpeedMult = statArray[user]
    return

def setStats(Player, opponent):
    # these global values need to be accessed by other functions
    global attackMult, defenseMult, spattackMult, spdefenseMult, speedMult
    global oppAttackMult, oppDefenseMult, oppSpattackMult, oppSpdefenseMult, oppSpeedMult
    # change the in-battle stat of the Pokemon to its base stat times the multiplier
    # could probably do this with arrays and for loops, but meh
    Player.current_pokemon.battleAttack = Player.current_pokemon.attack * stat_multipliers[attackMult]
    Player.current_pokemon.battleDefense = Player.current_pokemon.defense * stat_multipliers[defenseMult]
    Player.current_pokemon.battleSpattack = Player.current_pokemon.spattack * stat_multipliers[spattackMult]
    Player.current_pokemon.battleSpdefense = Player.current_pokemon.spdefense * stat_multipliers[spdefenseMult]
    Player.current_pokemon.battleSpeed = Player.current_pokemon.speed * stat_multipliers[speedMult]
    # same for opponent's Pokemon
    opponent.current_pokemon.battleAttack = opponent.current_pokemon.attack * stat_multipliers[oppAttackMult]
    opponent.current_pokemon.battleDefense = opponent.current_pokemon.defense * stat_multipliers[oppDefenseMult]
    opponent.current_pokemon.battleSpattack = opponent.current_pokemon.spattack * stat_multipliers[oppSpattackMult]
    opponent.current_pokemon.battleSpdefense = opponent.current_pokemon.spdefense * stat_multipliers[oppSpdefenseMult]
    opponent.current_pokemon.battleSpeed = opponent.current_pokemon.speed * stat_multipliers[oppSpeedMult]
    return

def playerHealthCheck(Player, opponent):
    # if the pokemon has less than 1 hp, force a switch. They won't be able to use the back button
    if Player.current_pokemon.battleHp <= 0:
        print(Player.name + "'s " + Player.current_pokemon.name + " fainted!")
        playerSwitch(Player, True)
        Turn(Player, opponent)
        return

def oppHealthCheck(opponent):
    # added this function to break up the giant Turn function. Very simple
    if opponent.current_pokemon.battleHp <= 0:
        print(f"{opponent.name}'s {opponent.current_pokemon.name} fainted!")
        opponent.current_pokemon = switch_on_faint(opponent)
        if opponent.current_pokemon is None:
            endBattle(Player)
            return
        return "Switched"
    return

def generateHealthBars(Player, opponent):
    # setting the increment of hp to be displayed to be 20
    hpMultiple = 20
    # every 20 health remaining is a hash, every 20 health missing is a space
    hashes = int(Player.current_pokemon.battleHp/hpMultiple)
    spaces = int((Player.current_pokemon.hp - Player.current_pokemon.battleHp)/hpMultiple)
    hashes = str(hashes * "#")
    spaces = str(spaces * "-")
    # so the final output looks like [###  ] where a hash is 20 hp and dash is 20 absent
    # I changed the spaces to be dashes because they look better but not changing the var name
    playerMonHealth = f"[{hashes}{spaces}]"
    # same for opponent
    hashes1 = int(opponent.current_pokemon.battleHp/hpMultiple)
    spaces1 = int((opponent.current_pokemon.hp - opponent.current_pokemon.battleHp)/hpMultiple)
    hashes1 = str(hashes1 * "#")
    spaces1 = str(spaces1 * "-")
    opponentMonHealth = f"[{hashes1}{spaces1}]"
    # then just printing out the respective health bars
    print(f"{Player.name}'s {Player.current_pokemon.name}:")
    print(f"{playerMonHealth}")
    print(f"{opponent.name}'s {opponent.current_pokemon.name}:")
    print(f"{opponentMonHealth}")
    return

def getInfo(Pokemon):
    # give information on the Pokemon selected. Helps me debug and useful for player
    print(f"{Pokemon.name}")
    # handling if pokemon has one or two types
    try:
        print(f"Type(s): {Pokemon.type[0].name}/{Pokemon.type[1].name}")
    except IndexError:
        print(f"Type: {Pokemon.type[0].name}")
    # print out the stats
    print(f"HP is: {Pokemon.battleHp}/{Pokemon.hp}")
    print(f"Attack is: {Pokemon.battleAttack}")
    print(f"Defense is: {Pokemon.battleDefense}")
    print(f"Special Attack is: {Pokemon.battleSpattack}")
    print(f"Special Defense is: {Pokemon.battleSpdefense}")
    print(f"Speed is: {Pokemon.battleSpeed}")
    return

def opponentTurn(Player, opponent):
    # basic, just choosing a random move and going through accuracy and damage calcs
    chosen_move = opponent.current_pokemon.moves[randint(0, (len(opponent.current_pokemon.moves) - 1))]
    if checkAccuracy(chosen_move, Player, opponent, 1) == 1:
        calcDamage(chosen_move, opponent, Player)
    return
          
def Turn(Player, opponent):
    global attackMult, defenseMult, spattackMult, spdefenseMult, speedMult
    global oppAttackMult, oppDefenseMult, oppSpattackMult, oppSpdefenseMult, oppSpeedMult
    # setting up this loop so the battle continues while the mons can fight
    # the loop was Copilot's suggestion
    while Player.current_pokemon.battleHp > 0 and opponent.current_pokemon.battleHp > 0:
        # set the stats based on the current multipliers
        setStats(Player, opponent)
        # output the health bars
        generateHealthBars(Player, opponent)
        print("What will you do?")
        print("1. Fight")
        print("2. Switch Pokemon")
        print("3. Info")
        # input error handling
        acceptable_inputs = [1, 2, 3]
        try:
            battle_choice = int(input("Choice: "))
        except ValueError:
            battle_choice = -1
        while battle_choice not in acceptable_inputs:
            print("Invalid selection.")
            try:
                battle_choice = int(input("Choice: "))
            except ValueError:
                battle_choice = -1
        # player switches, opponent gets to attack the new pokemon
        if battle_choice == 2:
            if playerSwitch(Player, False):
                opponentTurn(Player, opponent)
            continue
        # for the getInfo function
        if battle_choice == 3:
            print("Which Pokemon?")
            print(f"1. {Player.name}'s {Player.current_pokemon.name}")
            print(f"2. {opponent.name}'s {opponent.current_pokemon.name}")
            
            # more error handling
            try: 
                info_choice = input("Choice: ")
            except ValueError:
                info_choice = -1
            while info_choice not in ["1", "2"]:
                print("Invalid selection.")
                try: 
                    info_choice = input("Choice: ")
                except ValueError:
                    info_choice = -1
            if info_choice == "1":
                getInfo(Player.current_pokemon)
            elif info_choice == "2":
                getInfo(opponent.current_pokemon)
            continue
        # here's the horrible monolith I want to break up
        if battle_choice == 1:
            print("Use which move?")
            # print the moves, their power, and their accuracy
            for i in range(len(Player.current_pokemon.moves)):
                print(f"{str(i + 1)}. {Player.current_pokemon.moves[i].name} "
                      f"Type: {Player.current_pokemon.moves[i].type.name} "
                      f"Power: {str(Player.current_pokemon.moves[i].power)} "
                      f"Acc: {str(Player.current_pokemon.moves[i].accuracy)} "
                      f"({Player.current_pokemon.moves[i].moveType})")
            print(f"{len(Player.current_pokemon.moves) + 1}. Back")
            # input error handling
            try:
                move_index = int(input("Select move: ")) - 1
            except ValueError:
                move_index = -1
            while move_index not in range(len(Player.current_pokemon.moves) + 1):
                print("Invalid selection.")
                try:
                    move_index = int(input("Select move: ")) - 1
                except ValueError:
                    move_index = -1
            if move_index == len(Player.current_pokemon.moves):
                continue
            # If opponent is faster:
            if calcPriority(Player.current_pokemon.battleSpeed, opponent.current_pokemon.battleSpeed) == 1:
                opponentTurn(Player, opponent)
                playerHealthCheck(Player, opponent)
                if checkAccuracy(Player.current_pokemon.moves[move_index], Player, opponent, 0) == 1:
                    calcDamage(Player.current_pokemon.moves[move_index], Player, opponent)
                oppHealthCheck(opponent)
                
            # If player is faster
            else:
                if checkAccuracy(Player.current_pokemon.moves[move_index], Player, opponent, 0) == 1:
                    calcDamage(Player.current_pokemon.moves[move_index], Player, opponent)
                # health check returns Switched if it happens so opponent can't also move
                if oppHealthCheck(opponent) != "Switched":
                    opponentTurn(Player, opponent)
                    playerHealthCheck(Player, opponent)
        
def endBattle(winner):
    # very simple end battle call to close the program
    print(f"The battle is over! {winner.name} is the winner!")
    print("Thank you for playing! Would you like to restart?")
    # allow the user to restart with the same team if they wanted to
    acceptable_inputs = [1, 2]
    try: 
        restart = int(input("1. Yes\n2. No\n"))
    except ValueError:
        restart = -1
    while restart not in acceptable_inputs:
        print("Invalid selection.")
        try: 
            restart = int(input("1. Yes\n2. No\n"))
        except ValueError:
            restart = -1
    if restart == 2:
        # using sys.exit was a suggestion by Copilot
        sys.exit()
    elif restart == 1: 
        startBattle()
        Turn(Player, opponent)

def main():
    # main loop
    print("Welcome to Pokemon!")
    # start uop the battle and enter the turn
    initializeGame()
    startBattle()
    Turn(Player, opponent)

main()
