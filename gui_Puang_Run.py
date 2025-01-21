"""
내 캐릭터: "jjuang" (푸앙이 이미지)
프로그램 이름: Puang Run
게임 방법:
  - 게임 (재)시작: Enter 키
  - 점프: Space 키 
  - Stage 4 진입 후 즉시 착지 기능: Down 키
  - 치트 모드: C 키 
  - 게임 종료: Esc 키 
"""

import gui_core as gui
import random

w = gui.Window('Puang Run', 800, 400, interval=1/60)

def initialize(timestamp):
    w.data.state = 'start'  # 0: 시작상태
    try:
        if hasattr(w.data, 'player'):
            w.deleteObject(w.data.player)
        w.data.player = w.newImage(50, 300, 'jjuang.png', 40, 40)  # 내 캐릭터의 디자인(푸앙이 이미지)
    except Exception as e:
        print(f"Error loading image: {e}")
        w.stop()
        return

    # 이전 장애물 초기화 및 게임 restart
    if not hasattr(w.data, 'obstacles'):
        w.data.obstacles = []
    for obstacle in w.data.obstacles:
        try:
            w.deleteObject(obstacle)
        except AttributeError:
            pass
    w.data.obstacles = []

    w.data.spawn_timer = 0
    w.data.is_jumping = False
    w.data.jump_velocity = 0
    w.data.gravity = 0.5
    w.data.score = 0
    w.data.stage = 1
    w.data.notification_timer = None
    w.data.cheat_mode_timer = None  

    # UI 요소들
    if not hasattr(w.data, 'text_score'):
        w.data.text_score = w.newText(10, 10, 300, 'Score: 0', 'black', anchor='nw')
    else:
        w.setText(w.data.text_score, 'Score: 0')

    if not hasattr(w.data, 'text_stage'):
        w.data.text_stage = w.newText(700, 10, 300, 'Stage: 1', 'black', anchor='nw')
    else:
        w.setText(w.data.text_stage, 'Stage: 1')

    if not hasattr(w.data, 'text_stage_notification'):
        w.data.text_stage_notification = w.newText(400, 50, 300, '', 'blue', anchor='center')
    else:
        w.setText(w.data.text_stage_notification, '')

    if not hasattr(w.data, 'ground'):
        w.data.ground = w.newRectangle(0, 340, 800, 60, 'black')
    else:
        w.moveObject(w.data.ground, 0, 340)

    w.data.cheat_mode = False
    w.data.cheat_key_released = True  # C키를 통한 Cheat_mode ON / OFF

    if not hasattr(w.data, 'start_text'):
        w.data.start_text = w.newText(400, 200, 800, 'Press Enter to Start', 'black', anchor='center')
    else:
        w.showObject(w.data.start_text)

def update(timestamp):
    if w.keys['Escape']:
        w.stop()
        return
    
    if w.data.state == 'start':
        if w.keys['Return']:
            w.data.state = 'playing' # 1: 대기상태(Enter 입력시) --> 2: 출제상태(장애물 등장)
            w.hideObject(w.data.start_text)
            w.setTitle("You're now playing Puang Run!")  
        return

    if w.data.state == 'gameover': # 3: 결과확인상태(Game Over)
        if not hasattr(w.data, 'game_over_text'):
            w.data.game_over_text = w.newText(400, 200, 300, 'Game Over!', 'blue', anchor='center')
        else:
            w.showObject(w.data.game_over_text)
        if not hasattr(w.data, 'game_over_audio_played') or not w.data.game_over_audio_played:
            try:
                w.playSound('sample.wav')
                w.data.game_over_audio_played = True
            except Exception as e:
                print(f"Error playing sound: {e}")
        if w.keys['Return']:
            w.data.state = 'start' # 0: 시작상태(Enter 입력시)로 역행
            w.hideObject(w.data.game_over_text)
            w.data.game_over_audio_played = False
            initialize(timestamp)
        return

    # Cheat_mode 조작
    if w.keys['c']:
        if w.data.cheat_key_released:  # Ensure key is released before toggling
            w.data.cheat_mode = not w.data.cheat_mode
            if w.data.cheat_mode:
                w.setTitle('Cheat Mode: ON')
                w.data.cheat_mode_timer = None  
            else:
                w.setTitle('Cheat Mode: OFF')
                w.data.cheat_mode_timer = 120  
            w.data.cheat_key_released = False
    else:
        w.data.cheat_key_released = True

    # Cheat_mode Title명 상태
    if w.data.cheat_mode_timer is not None: 
        w.data.cheat_mode_timer -= 1
        if w.data.cheat_mode_timer <= 0:
            w.setTitle("You're now playing Puang Run!")  
            w.data.cheat_mode_timer = None

    # 내 캐릭터 점프
    x, y = w.getPosition(w.data.player)

    if w.keys['space'] and not w.data.is_jumping:
        w.data.is_jumping = True
        w.data.jump_velocity = 10

    if w.data.is_jumping:
        w.data.jump_velocity -= w.data.gravity
        y -= w.data.jump_velocity

        # 활공(점프)상태에서의 즉시 착지
        if y >= 300:
            y = 300
            w.data.is_jumping = False
            w.data.jump_velocity = 0

    # 스테이지4 진입시 즉시 착지 가능
    if w.keys['Down'] and w.data.stage >= 4 and w.data.is_jumping:
        y = 300
        w.data.is_jumping = False
        w.data.jump_velocity = 0

    w.moveObject(w.data.player, x, y)

    # 장애물 생성
    w.data.spawn_timer += 1
    if w.data.spawn_timer > max(100 - w.data.stage * 10, 20):
        random_color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        new_obstacle = w.newRectangle(800, 300, 40, 40, random_color)  # Ground obstacle with random color
        w.data.obstacles.append(new_obstacle)
        w.data.spawn_timer = 0

    # 장애물 이동
    for obstacle in w.data.obstacles[:]:
        ox, oy = w.getPosition(obstacle)
        w.moveObject(obstacle, ox - (5 + w.data.stage), oy)

        # 통과한 장애물 제거
        if ox < -40:
            w.data.obstacles.remove(obstacle)
            w.deleteObject(obstacle)
            w.data.score += 10  # Increment score by 10 per obstacle

            # 스테이지 진전도
            if w.data.score % 100 == 0:
                w.data.stage += 1
                w.setText(w.data.text_stage, f'Stage: {w.data.stage}')
                if w.data.stage == 4:
                    w.setText(w.data.text_stage_notification, "Stage 4! 이제 바로 착지할 수 있습니다!")
                else:
                    w.setText(w.data.text_stage_notification, f"Stage {w.data.stage}!")
                w.showObject(w.data.text_stage_notification)
                w.data.notification_timer = 120  # Set timer for 2 seconds (assuming 60 FPS)

    # Cheat_mode Title명 상태 timer
    if w.data.notification_timer is not None:
        w.data.notification_timer -= 1
        if w.data.notification_timer <= 0:
            w.hideObject(w.data.text_stage_notification)
            w.data.notification_timer = None

    # 점수 업데이트
    w.setText(w.data.text_score, f'Score: {w.data.score}')

    # 충돌했을 때
    if not w.data.cheat_mode:
        for obstacle in w.data.obstacles:
            ox, oy = w.getPosition(obstacle)
            px, py = w.getPosition(w.data.player)
            player_top = py
            player_bottom = py + 40
            obstacle_top = oy
            obstacle_bottom = oy + 40

            if (player_bottom > obstacle_top and player_top < obstacle_bottom and
                px + 40 > ox and px < ox + 40):
                w.data.state = 'gameover'
                w.setTitle('Game Over! Press Enter to Restart')

w.initialize = initialize
w.update = update

w.start()

