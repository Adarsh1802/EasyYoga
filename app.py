import json
import hashlib
import random
import webbrowser
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.config import Config
from kivy.lang import Builder

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '600')
Config.write()

USER_DATA_FILE = 'user_data.json'
YOGA_POSES_FILE = 'chair_yoga_poses.json'

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            data = file.read().strip()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, notification_time, remember_me):
    user_data = load_user_data()
    if username in user_data:
        print("Username already exists. Please choose a different username.")
        return False
    user_data[username] = {
        "password": hash_password(password),
        "notification_time": notification_time,
        "remember_me": remember_me
    }
    save_user_data(user_data)
    print(f"User {username} registered successfully.")
    return True

def login_user(username, password):
    user_data = load_user_data()
    if username in user_data and user_data[username]["password"] == hash_password(password):
        print(f"User {username} logged in successfully.")
        return True
    print("Invalid username or password.")
    return False

def get_logged_in_user():
    try:
        with open('current_user.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def set_logged_in_user(username):
    with open('current_user.txt', 'w') as file:
        file.write(username)

def logout_user():
    with open('current_user.txt', 'w') as file:
        file.write('')

def load_yoga_poses():
    try:
        with open(YOGA_POSES_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def recommend_yoga_poses(poses, days=1, poses_per_day=3):
    schedule = []
    for _ in range(days):
        day_schedule = random.sample(poses, poses_per_day)
        schedule.append(day_schedule)
    return schedule

class WelcomeScreen(MDScreen):
    pass

class LoginScreen(MDScreen):
    pass

class DashboardScreen(MDScreen):
    recommended_poses = None

    def on_pre_enter(self):
        username = get_logged_in_user()
        self.ids.welcome_label.text = f"Welcome, {username}"

        if DashboardScreen.recommended_poses is None:
            poses = load_yoga_poses()
            schedule = recommend_yoga_poses(poses, days=1)
            DashboardScreen.recommended_poses = schedule[0]

        for i, pose in enumerate(DashboardScreen.recommended_poses, start=1):
            self.ids[f"pose_name_{i}"].text = pose["name"]

class YogaPoseScreen(MDScreen):
    def on_enter(self, pose_index=0):
        self.pose_index = pose_index
        self.show_pose(self.pose_index)

    def show_pose(self, pose_index):
        poses = DashboardScreen.recommended_poses
        pose = poses[pose_index]

        self.ids.pose_name.text = pose["name"]
        self.ids.pose_description.text = pose["description"]
        self.youtube_link = pose.get("youtube_link", "")

    def open_youtube_video(self):
        webbrowser.open(self.youtube_link)

    def next_pose(self):
        if self.pose_index < 2:
            self.pose_index += 1
            self.show_pose(self.pose_index)
        else:
            self.manager.current = "completion"

class SignUpScreen(MDScreen):
    pass

class CompletionScreen(MDScreen):
    pass

class PoseDetailScreen(MDScreen):
    def set_pose_details(self, pose):
        self.ids.detail_pose_name.text = pose["name"]
        self.ids.detail_pose_description.text = pose["description"]
        self.ids.detail_pose_benefits.text = pose["benefits"]
        self.youtube_link = pose.get("youtube_link", "")

    def open_youtube_video(self):
        webbrowser.open(self.youtube_link)

class SettingsScreen(MDScreen):
    pass

class VideoScreen(MDScreen):
    def set_video(self, url):
        video_player = self.ids.video_player
        video_player.source = url
        video_player.state = 'play'
        video_player.options = {'eos': 'loop'}

    def on_pre_enter(self):
        if 'video_player' in self.ids:
            self.ids.video_player.state = 'play'

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.primary_hue = "700"
        return Builder.load_file('login.kv')

    def login(self, username, password):
        if login_user(username, password):
            set_logged_in_user(username)
            self.root.current = "dashboard"
        else:
            print("Invalid credentials")

    def sign_up(self, username, password, confirm_password, remember_me):
        if password != confirm_password:
            print("Passwords do not match")
            return

        if register_user(username, password, None, remember_me):
            set_logged_in_user(username)
            self.root.current = "dashboard"

    def go_to_sign_up(self):
        self.root.current = "sign_up"

    def forgot_password(self):
        print("Forgot password button pressed")

    def login_facebook(self):
        print("Facebook login button pressed")

    def login_google(self):
        print("Google login button pressed")

    def play(self):
        self.root.current = "yoga_pose"
        self.root.get_screen("yoga_pose").on_enter()

    def next_pose(self):
        self.root.get_screen("yoga_pose").next_pose()

    def go_back(self):
        if self.root.current == 'login':
            self.root.current = 'welcome'
        elif self.root.current == 'dashboard':
            self.root.current = 'login'
        elif self.root.current == 'yoga_pose':
            self.root.current = 'dashboard'
        elif self.root.current == 'pose_detail':
            self.root.current = 'dashboard'
        elif self.root.current == 'video_screen':
            self.root.current = 'pose_detail'
        elif self.root.current == 'sign_up':
            self.root.current = 'login'
        elif self.root.current == 'settings':
            self.root.current = 'dashboard'

    def show_pose_details(self, pose_index):
        pose = DashboardScreen.recommended_poses[pose_index]
        pose_detail_screen = self.root.get_screen("pose_detail")
        pose_detail_screen.set_pose_details(pose)
        self.root.current = "pose_detail"

    def go_to_settings(self):
        self.root.current = "settings"

    def save_notification_time(self, hour, minute):
        username = get_logged_in_user()
        user_data = load_user_data()
        if username in user_data:
            user_data[username]['notification_time'] = f"{hour}:{minute}"
            save_user_data(user_data)
            print(f"Notification time set to {hour}:{minute} for user {username}")
        self.go_back()

if __name__ == '__main__':
    MainApp().run()
