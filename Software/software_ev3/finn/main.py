'''{from pybricks.tools import StopWatch, wait
from robot import Robot

# Testfahrt
bot = Robot()

#meine struktur ist etwas anders, ich habe alle software instanzen in einer roboter klasse (hier bot)
#ich glaube der rest ist selbsterklärend. nur wenn er bergab geht bekommt man für die selbe
# steigung eine kleiner abweichung von 215° (wenn man eben fährt), deshalb *1.5 
#20/12 wegen dem übersetzungsverhältnis der zahnräder am motor
#0.18 ist die konstante dmait man vom motorwiderstand auf den winkel kommt
    bot.left_motor.dc(30)
    bot.right_motor.dc(30)
    
    value = (bot.left_motor.speed() + bot.right_motor.speed())/2
    power = (215 - value) * 0.18 * 20/12
    if power < 0 :
        power *= 1.5

    print(bot.left_motor.speed(), bot.right_motor.speed(), value, power )

    bot.balance_motor.run_target(100, power, then=Stop.COAST, wait = False)}'''