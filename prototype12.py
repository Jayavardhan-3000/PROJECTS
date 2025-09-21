import cv2 as cv
import mediapipe as mp
import numpy as np
import math
import time
import random
import customtkinter as ctk
from PIL import Image, ImageTk

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Set appearance mode and custom monoblack theme
ctk.set_appearance_mode("dark")

# Custom colors for the monoblack theme
MONOBLACK_COLORS = {
    "background": "#121212",
    "card_bg": "#1e1e1e",
    "card_border": "#00ffff",  # Vibrant cyan for neon glow effect
    "accent_green": "#4caf50",
    "text_white": "#ffffff",
    "text_gray": "#aaaaaa"
}
ctk.set_default_color_theme("green") # Still use green for button hover/click effects

# --- Exercise and Motivational Data ---
# Body goal types with programs and descriptions
BODY_GOALS = {
    "weight_loss": {
        "name": "Weight Loss",
        "description": "High-rep, full-body exercises to burn calories.",
        "programs": [
            {"name": "Beginner Fat Burn", "exercises": ["squat", "bicep_curl"], "sets": 3, "reps": 12},
            {"name": "Intermediate Cardio Blast", "exercises": ["squat", "shoulder_press", "bicep_curl"], "sets": 4, "reps": 15},
            {"name": "Advanced HIIT", "exercises": ["squat", "shoulder_press"], "sets": 5, "reps": 20}
        ],
        "calorie_adjustment": -500
    },
    "muscle_gain": {
        "name": "Muscle Gain",
        "description": "Strength training with progressive overload.",
        "programs": [
            {"name": "Beginner Strength", "exercises": ["bicep_curl", "shoulder_press"], "sets": 3, "reps": 8},
            {"name": "Intermediate Hypertrophy", "exercises": ["bicep_curl", "shoulder_press", "squat"], "sets": 4, "reps": 10},
            {"name": "Advanced Power Building", "exercises": ["squat", "shoulder_press"], "sets": 5, "reps": 6}
        ],
        "calorie_adjustment": 300
    },
    "endurance": {
        "name": "Endurance",
        "description": "Building muscular endurance and stamina.",
        "programs": [
            {"name": "Beginner Endurance", "exercises": ["squat", "bicep_curl"], "sets": 3, "reps": 15},
            {"name": "Intermediate Stamina", "exercises": ["squat", "shoulder_press", "bicep_curl"], "sets": 4, "reps": 20},
            {"name": "Advanced Marathon", "exercises": ["squat", "shoulder_press"], "sets": 5, "reps": 25}
        ],
        "calorie_adjustment": 0
    },
    "toning": {
        "name": "Toning",
        "description": "Sculpting and defining muscles.",
        "programs": [
            {"name": "Beginner Tone", "exercises": ["bicep_curl", "squat"], "sets": 3, "reps": 12},
            {"name": "Intermediate Sculpt", "exercises": ["bicep_curl", "shoulder_press", "squat"], "sets": 4, "reps": 15},
            {"name": "Advanced Definition", "exercises": ["shoulder_press", "squat"], "sets": 4, "reps": 15}
        ],
        "calorie_adjustment": 0
    },
    "athletic": {
        "name": "Athletic Build",
        "description": "Compound exercises for overall strength.",
        "programs": [
            {"name": "Beginner Athletic", "exercises": ["push_up", "squat"], "sets": 3, "reps": 8},
            {"name": "Intermediate Athletic", "exercises": ["push_up", "squat", "bicep_curl"], "sets": 4, "reps": 10},
            {"name": "Advanced Athletic", "exercises": ["push_up", "squat", "shoulder_press"], "sets": 4, "reps": 12}
        ],
        "calorie_adjustment": 0
    },
    "core_strength": {
        "name": "Core Strength",
        "description": "Building a strong core and abs.",
        "programs": [
            {"name": "Beginner Core", "exercises": ["plank", "squat"], "sets": 3, "reps": 10},
            {"name": "Intermediate Core", "exercises": ["plank", "squat", "push_up"], "sets": 4, "reps": 12},
            {"name": "Advanced Core", "exercises": ["plank", "push_up", "squat"], "sets": 4, "reps": 15}
        ],
        "calorie_adjustment": 0
    },
    "flexibility": {
        "name": "Flexibility",
        "description": "Improving range of motion and flexibility.",
        "programs": [
            {"name": "Beginner Flexibility", "exercises": ["stretch", "squat"], "sets": 3, "reps": 8},
            {"name": "Intermediate Flexibility", "exercises": ["stretch", "squat", "push_up"], "sets": 3, "reps": 10},
            {"name": "Advanced Flexibility", "exercises": ["stretch", "push_up", "squat"], "sets": 4, "reps": 12}
        ],
        "calorie_adjustment": 0
    }
}

# Exercise definitions
EXERCISES = {
    "bicep_curl": {
        "name": "Bicep Curl",
        "logic": "bicep_curl_logic",
        "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"],
        "instructions": "1. Stand straight with arms by your side\n2. Curl your forearm up towards your shoulder\n3. Slowly lower back to starting position"
    },
    "shoulder_press": {
        "name": "Shoulder Press",
        "logic": "shoulder_press_logic",
        "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"],
        "instructions": "1. Start with elbows bent at 90 degrees\n2. Press upward until arms are fully extended\n3. Slowly return to starting position"
    },
    "squat": {
        "name": "Squat",
        "logic": "squat_logic",
        "landmarks": ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"],
        "instructions": "1. Stand with feet shoulder-width apart\n2. Lower your hips as if sitting in a chair\n3. Keep your chest up and knees behind toes\n4. Return to standing position"
    },
    "push_up": {
        "name": "Push Up",
        "logic": "push_up_logic",
        "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"],
        "instructions": "1. Start in a plank position with hands shoulder-width apart\n2. Lower your body until chest nearly touches the floor\n3. Push back up to the starting position"
    },
    "plank": {
        "name": "Plank",
        "logic": "plank_logic",
        "landmarks": ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_ANKLE"],
        "instructions": "1. Start in a push-up position with weight on forearms\n2. Keep your body in a straight line from head to heels\n3. Hold this position for the required time"
    },
    "stretch": {
        "name": "Full Body Stretch",
        "logic": "stretch_logic",
        "landmarks": ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_ANKLE"],
        "instructions": "1. Stand with feet shoulder-width apart\n2. Reach arms overhead and stretch upward\n3. Bend at the waist and reach toward your toes\n4. Return to standing position"
    }
}

MOTIVATIONAL_QUOTES = [
    "KEEP GOING! YOU'VE GOT THIS!",
    "DON'T GIVE UP! YOU'RE STRONGER THAN YOU THINK!",
    "PUSH THROUGH THE PAIN! GROWTH IS ON THE OTHER SIDE!",
    "ONE MORE REP! YOU CAN DO IT!",
    "YOUR FUTURE SELF WILL THANK YOU!",
    "STRENGTH DOESN'T COME FROM WHAT YOU CAN DO, IT COMES FROM OVERCOMING WHAT YOU ONCE THOUGHT YOU COULDN'T!",
    "THE ONLY BAD WORKOUT IS THE ONE THAT DIDN'T HAPPEN!"
]

# --- Main Application Class ---
class FitnessApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Fitness Coach")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.root.configure(fg_color=MONOBLACK_COLORS["background"])
        
        # Initialize variables
        self.counter = 0
        self.stage = None
        self.last_rep_time = time.time()
        self.LONG_REST_THRESHOLD = 5
        self.motivation_played = False
        self.current_exercise = None
        self.current_quote = "SELECT YOUR FITNESS GOAL TO BEGIN"
        self.quote_display_time = time.time()
        self.cap = None
        self.is_camera_active = False
        self.user_goal = None
        self.selected_program = None
        self.current_set = 1
        self.workout_in_progress = False
        self.exercise_index = 0
        
        # Load custom fonts
        self.font_title = ctk.CTkFont(family="Inter", size=36, weight="bold")
        self.font_header = ctk.CTkFont(family="Inter", size=24, weight="bold")
        self.font_medium = ctk.CTkFont(family="Inter", size=16, weight="bold")
        self.font_small = ctk.CTkFont(family="Inter", size=12)
        
        # Setup the main UI
        self.setup_ui()
        
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self.root, fg_color=MONOBLACK_COLORS["background"])
        self.main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        self.setup_main_menu()

    def setup_main_menu(self):
        self.clear_frame(self.main_container)
        
        # Main Title Frame
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(20, 0), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(title_frame, text="AI FITNESS COACH", font=self.font_title, text_color=MONOBLACK_COLORS["accent_green"])
        title_label.grid(row=0, column=0, pady=(10, 5))
        
        subtitle_label = ctk.CTkLabel(title_frame, text="Select a fitness goal or track your calories.", font=self.font_medium, text_color=MONOBLACK_COLORS["text_gray"])
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Main Menu Buttons
        menu_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        menu_frame.grid(row=1, column=0, pady=10)
        
        workout_btn = ctk.CTkButton(menu_frame, text="Start Workout", command=self.setup_goal_selection, font=self.font_medium, height=40, width=200)
        workout_btn.pack(side="left", padx=10, pady=10)
        
        calorie_btn = ctk.CTkButton(menu_frame, text="Calorie Tracker", command=self.setup_calorie_tracker, font=self.font_medium, height=40, width=200)
        calorie_btn.pack(side="left", padx=10, pady=10)
        
    def setup_goal_selection(self):
        self.clear_frame(self.main_container)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(20, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="SELECT YOUR GOAL", font=self.font_header, text_color=MONOBLACK_COLORS["accent_green"])
        title_label.grid(row=0, column=0, pady=(10, 5))
        
        subtitle_label = ctk.CTkLabel(header_frame, text="Choose a goal to get your custom workout plan.", font=self.font_medium, text_color=MONOBLACK_COLORS["text_gray"])
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Goals Frame with improved spacing and a fixed height for scrolling
        goals_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", height=400)
        goals_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        goals_frame.grid_columnconfigure((0, 1, 2), weight=1, minsize=250)
        
        row, col = 0, 0
        for goal_key, goal_data in BODY_GOALS.items():
            goal_card = ctk.CTkFrame(
                goals_frame, 
                corner_radius=15, 
                fg_color=MONOBLACK_COLORS["card_bg"],
                border_width=2,
                border_color=MONOBLACK_COLORS["card_border"]
            )
            goal_card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            goal_card.grid_columnconfigure(0, weight=1)
            
            name_label = ctk.CTkLabel(goal_card, text=goal_data["name"], font=self.font_medium)
            name_label.grid(row=0, column=0, pady=(20, 5))
            
            desc_label = ctk.CTkLabel(goal_card, text=goal_data["description"], font=self.font_small, wraplength=200, justify="center", text_color=MONOBLACK_COLORS["text_gray"])
            desc_label.grid(row=1, column=0, padx=10, pady=(0, 10))
            
            select_btn = ctk.CTkButton(
                goal_card, 
                text="Select", 
                command=lambda gk=goal_key: self.select_goal(gk), 
                height=30,
                corner_radius=8,
                fg_color=MONOBLACK_COLORS["accent_green"],
                hover_color="#458a48"
            )
            select_btn.grid(row=2, column=0, pady=(0, 15), padx=20, sticky="ew")

            col += 1
            if col > 2: # 3 cards per row
                col = 0
                row += 1

        back_btn = ctk.CTkButton(self.main_container, text="← Back to Menu", command=self.setup_main_menu, font=self.font_small, width=150, fg_color="transparent")
        back_btn.grid(row=2, column=0, pady=10, sticky="w")

    def select_goal(self, goal_key):
        self.user_goal = goal_key
        self.show_program_selection()
    
    def setup_calorie_tracker(self):
        self.clear_frame(self.main_container)
        
        main_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Calorie Tracker Card
        tracker_card = ctk.CTkFrame(
            main_frame,
            corner_radius=15,
            fg_color=MONOBLACK_COLORS["card_bg"],
            border_width=2,
            border_color=MONOBLACK_COLORS["card_border"]
        )
        tracker_card.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        tracker_card.grid_columnconfigure(0, weight=1)
        tracker_card.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(tracker_card, text="CALORIE TRACKER", font=self.font_header, text_color=MONOBLACK_COLORS["accent_green"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))
        
        # Input Fields
        input_frame = ctk.CTkFrame(tracker_card, fg_color="transparent")
        input_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(input_frame, text="Age:", font=self.font_medium).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.age_entry = ctk.CTkEntry(input_frame, width=100)
        self.age_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="Height (cm):", font=self.font_medium).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.height_entry = ctk.CTkEntry(input_frame, width=100)
        self.height_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="Weight (kg):", font=self.font_medium).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.weight_entry = ctk.CTkEntry(input_frame, width=100)
        self.weight_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="Activity Level:", font=self.font_medium).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.activity_level_var = ctk.StringVar(value="Sedentary")
        activity_option_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.activity_level_var,
            values=["Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"]
        )
        activity_option_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        gender_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        gender_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(gender_frame, text="Gender:", font=self.font_medium).pack(side="left", padx=(0, 10))
        self.gender_var = ctk.StringVar(value="Male")
        male_radio = ctk.CTkRadioButton(gender_frame, text="Male", variable=self.gender_var, value="Male")
        male_radio.pack(side="left", padx=5)
        female_radio = ctk.CTkRadioButton(gender_frame, text="Female", variable=self.gender_var, value="Female")
        female_radio.pack(side="left", padx=5)
        
        # New Goal Selection for Calorie Tracker
        ctk.CTkLabel(input_frame, text="Body Goal:", font=self.font_medium).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.goal_var = ctk.StringVar(value=BODY_GOALS["weight_loss"]["name"])
        goal_option_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.goal_var,
            values=[goal["name"] for goal in BODY_GOALS.values()]
        )
        goal_option_menu.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        calculate_btn = ctk.CTkButton(tracker_card, text="Calculate", command=self.calculate_calories, font=self.font_medium, fg_color=MONOBLACK_COLORS["accent_green"])
        calculate_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Result Labels
        self.results_frame = ctk.CTkFrame(tracker_card, fg_color="transparent")
        self.results_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        self.result_label = ctk.CTkLabel(self.results_frame, text="Enter your details to calculate.", font=self.font_medium, text_color=MONOBLACK_COLORS["text_gray"])
        self.result_label.grid(row=0, column=0, pady=(0, 5))
        
        self.maintenance_label = ctk.CTkLabel(self.results_frame, text="", font=self.font_header, text_color=MONOBLACK_COLORS["text_white"])
        self.maintenance_label.grid(row=1, column=0, pady=(5, 5))
        
        self.goal_calories_label = ctk.CTkLabel(self.results_frame, text="", font=self.font_header, text_color=MONOBLACK_COLORS["accent_green"])
        self.goal_calories_label.grid(row=2, column=0, pady=(5, 5))
        
        self.goal_desc_label = ctk.CTkLabel(self.results_frame, text="", font=self.font_small, wraplength=400, justify="center", text_color=MONOBLACK_COLORS["text_gray"])
        self.goal_desc_label.grid(row=3, column=0, pady=(5, 5))
        
        # Back Button
        back_btn = ctk.CTkButton(self.main_container, text="← Back to Menu", command=self.setup_main_menu, font=self.font_small, width=150, fg_color="transparent")
        back_btn.grid(row=1, column=0, pady=10, sticky="w")

    def calculate_calories(self):
        try:
            age = int(self.age_entry.get())
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            gender = self.gender_var.get()
            activity_level = self.activity_level_var.get()
            
            # Harris-Benedict Equation for BMR
            if gender == "Male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else: # Female
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
            # Activity level multipliers
            activity_multipliers = {
                "Sedentary": 1.2,
                "Lightly active": 1.375,
                "Moderately active": 1.55,
                "Very active": 1.725,
                "Extra active": 1.9
            }
            
            maintenance_calories = int(bmr * activity_multipliers[activity_level])
            
            # Find the selected goal and calculate Goal Calories
            selected_goal_name = self.goal_var.get()
            selected_goal_key = next((key for key, value in BODY_GOALS.items() if value['name'] == selected_goal_name), None)
            
            if selected_goal_key:
                adjustment = BODY_GOALS[selected_goal_key]["calorie_adjustment"]
                goal_calories = maintenance_calories + adjustment
                
                self.maintenance_label.configure(text=f"Maintenance Calories: {maintenance_calories} cal", text_color=MONOBLACK_COLORS["text_white"])
                self.goal_calories_label.configure(text=f"Goal Calories: {goal_calories} cal", text_color=MONOBLACK_COLORS["accent_green"])
                
                if adjustment > 0:
                    desc_text = f"To gain muscle, aim for a daily surplus of {adjustment} calories."
                elif adjustment < 0:
                    desc_text = f"To lose weight, aim for a daily deficit of {abs(adjustment)} calories."
                else:
                    desc_text = "For this goal, maintaining your current calorie intake is key."
                
                self.goal_desc_label.configure(text=desc_text)
                self.result_label.configure(text="Results:")
                
        except ValueError:
            self.maintenance_label.configure(text="", text_color=MONOBLACK_COLORS["text_white"])
            self.goal_calories_label.configure(text="", text_color=MONOBLACK_COLORS["accent_green"])
            self.goal_desc_label.configure(text="")
            self.result_label.configure(text="Invalid input. Please enter numbers.", text_color="#dc3545")

    def show_program_selection(self):
        self.clear_frame(self.main_container)
        
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        back_btn = ctk.CTkButton(header_frame, text="← Back", command=self.setup_goal_selection, width=100)
        back_btn.grid(row=0, column=0, sticky="w")
        
        title_label = ctk.CTkLabel(header_frame, text=f"Programs for {BODY_GOALS[self.user_goal]['name']}", font=self.font_header)
        title_label.grid(row=0, column=1, padx=(10, 0))
        
        programs_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        programs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        programs_frame.grid_columnconfigure(0, weight=1)

        for i, program in enumerate(BODY_GOALS[self.user_goal]['programs']):
            program_card = ctk.CTkFrame(
                programs_frame, 
                corner_radius=15, 
                fg_color=MONOBLACK_COLORS["card_bg"],
                border_width=2,
                border_color=MONOBLACK_COLORS["card_border"]
            )
            program_card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            program_card.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(program_card, text=program['name'], font=self.font_medium)
            name_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
            
            details_label = ctk.CTkLabel(program_card, text=f"Sets: {program['sets']} | Reps: {program['reps']}", font=self.font_small, text_color=MONOBLACK_COLORS["text_gray"])
            details_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
            
            exercises = ", ".join([EXERCISES[ex]['name'] for ex in program['exercises']])
            ex_label = ctk.CTkLabel(program_card, text=f"Exercises: {exercises}", font=self.font_small, wraplength=500, justify="left", text_color=MONOBLACK_COLORS["text_gray"])
            ex_label.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="w")
            
            select_btn = ctk.CTkButton(
                program_card, 
                text="Start Program", 
                command=lambda p=program: self.select_program(p), 
                height=30,
                corner_radius=8,
                fg_color=MONOBLACK_COLORS["accent_green"],
                hover_color="#458a48"
            )
            select_btn.grid(row=3, column=0, pady=(0, 15), padx=20, sticky="ew")

    def select_program(self, program):
        self.selected_program = program
        self.show_workout_preview()

    def show_workout_preview(self):
        self.clear_frame(self.main_container)

        preview_panel = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=MONOBLACK_COLORS["card_bg"], border_width=2, border_color=MONOBLACK_COLORS["card_border"])
        preview_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        preview_panel.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(preview_panel, text=self.selected_program['name'], font=self.font_header)
        title.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        details_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        details_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)

        sets_label = ctk.CTkLabel(details_frame, text=f"Sets\n{self.selected_program['sets']}", font=self.font_medium, justify="center")
        sets_label.grid(row=0, column=0, padx=10, pady=10)
        
        reps_label = ctk.CTkLabel(details_frame, text=f"Reps\n{self.selected_program['reps']}", font=self.font_medium, justify="center")
        reps_label.grid(row=0, column=1, padx=10, pady=10)

        exercises_title = ctk.CTkLabel(preview_panel, text="Exercises in this program:", font=self.font_medium)
        exercises_title.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        
        ex_list_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        ex_list_frame.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="w")

        for exercise_key in self.selected_program['exercises']:
            exercise_name = EXERCISES[exercise_key]['name']
            ex_label = ctk.CTkLabel(ex_list_frame, text=f"• {exercise_name}", font=self.font_small, text_color=MONOBLACK_COLORS["text_gray"])
            ex_label.pack(anchor="w", pady=2)
            
        btn_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(0, 20))
        
        start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Workout",
            command=self.start_workout,
            height=50,
            font=self.font_medium,
            fg_color=MONOBLACK_COLORS["accent_green"],
            hover_color="#458a48"
        )
        start_btn.pack(side="left", padx=5)
        
        back_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.show_program_selection,
            height=50,
            fg_color="#333333",
            hover_color="#555555"
        )
        back_btn.pack(side="left", padx=5)

    def start_workout(self):
        self.workout_in_progress = True
        self.current_set = 1
        self.exercise_index = 0
        self.counter = 0
        self.current_exercise = self.selected_program['exercises'][self.exercise_index]
        
        self.show_workout_ui()
        self.start_camera()

    def show_workout_ui(self):
        self.clear_frame(self.main_container)
        
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Camera frame
        self.camera_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=MONOBLACK_COLORS["card_bg"], border_width=2, border_color=MONOBLACK_COLORS["card_border"])
        self.camera_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_rowconfigure(0, weight=1)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="Camera feed will appear here", font=self.font_medium, text_color=MONOBLACK_COLORS["text_gray"])
        self.camera_label.grid(row=0, column=0, sticky="nsew")
        
        # Info panel
        self.info_panel = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=MONOBLACK_COLORS["card_bg"], border_width=2, border_color=MONOBLACK_COLORS["card_border"])
        self.info_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.info_panel.grid_columnconfigure(0, weight=1)

        set_label = ctk.CTkLabel(self.info_panel, text=f"SET {self.current_set}/{self.selected_program['sets']}", font=self.font_medium, text_color=MONOBLACK_COLORS["text_gray"])
        set_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        ex_name = EXERCISES[self.current_exercise]['name'].upper()
        ex_label = ctk.CTkLabel(self.info_panel, text=ex_name, font=ctk.CTkFont(family="Inter", size=28, weight="bold"), text_color=MONOBLACK_COLORS["accent_green"])
        ex_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        self.reps_label = ctk.CTkLabel(self.info_panel, text=f"{self.counter}/{self.selected_program['reps']}", font=ctk.CTkFont(family="Inter", size=70, weight="bold"), text_color=MONOBLACK_COLORS["text_white"])
        self.reps_label.grid(row=2, column=0, padx=20, pady=10)

        instructions_title = ctk.CTkLabel(self.info_panel, text="INSTRUCTIONS", font=self.font_medium, text_color=MONOBLACK_COLORS["accent_green"])
        instructions_title.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")
        
        instructions_text = EXERCISES[self.current_exercise]['instructions']
        instructions_label = ctk.CTkLabel(self.info_panel, text=instructions_text, font=self.font_small, justify="left", wraplength=400, text_color=MONOBLACK_COLORS["text_gray"])
        instructions_label.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="w")
        
        self.next_exercise_btn = ctk.CTkButton(
            self.info_panel,
            text="NEXT EXERCISE",
            command=self.next_exercise,
            state="disabled",
            height=50,
            font=self.font_medium,
            fg_color=MONOBLACK_COLORS["accent_green"],
            hover_color="#458a48"
        )
        self.next_exercise_btn.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        finish_btn = ctk.CTkButton(
            self.info_panel,
            text="FINISH WORKOUT",
            command=self.finish_workout,
            fg_color="#dc3545",
            hover_color="#c82333",
            height=50,
            font=self.font_medium
        )
        finish_btn.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

    def next_exercise(self):
        self.exercise_index += 1
        self.counter = 0
        self.last_rep_time = time.time()
        self.motivation_played = False
        
        if self.exercise_index >= len(self.selected_program['exercises']):
            self.exercise_index = 0
            self.current_set += 1
            if self.current_set > self.selected_program['sets']:
                self.finish_workout()
                return
                
        self.current_exercise = self.selected_program['exercises'][self.exercise_index]
        self.show_workout_ui()

    def finish_workout(self):
        self.workout_in_progress = False
        self.stop_camera()
        
        self.clear_frame(self.main_container)

        finish_panel = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=MONOBLACK_COLORS["card_bg"], border_width=2, border_color=MONOBLACK_COLORS["card_border"])
        finish_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        finish_panel.grid_columnconfigure(0, weight=1)
        finish_panel.grid_rowconfigure(0, weight=1)

        title = ctk.CTkLabel(finish_panel, text="🎉 WORKOUT COMPLETED! 🎉", font=self.font_header, text_color=MONOBLACK_COLORS["accent_green"])
        title.grid(row=0, column=0, padx=20, pady=(40, 10))

        quote = ctk.CTkLabel(finish_panel, text=random.choice(MOTIVATIONAL_QUOTES), font=self.font_medium, wraplength=600, justify="center", text_color=MONOBLACK_COLORS["text_gray"])
        quote.grid(row=1, column=0, padx=20, pady=20)

        new_btn = ctk.CTkButton(
            finish_panel,
            text="START NEW WORKOUT",
            command=self.setup_main_menu,
            height=50,
            font=self.font_medium,
            fg_color=MONOBLACK_COLORS["accent_green"],
            hover_color="#458a48"
        )
        new_btn.grid(row=2, column=0, pady=30, padx=20, sticky="ew")
        
    def start_camera(self):
        if self.cap is None:
            # Try a few common camera indices to find a working one
            camera_index = 1
            for i in range(3):
                temp_cap = cv.VideoCapture(i)
                if temp_cap.isOpened():
                    camera_index = i
                    temp_cap.release()
                    break
            
            if camera_index != -1:
                self.cap = cv.VideoCapture(camera_index)
                print(f"Camera opened with index {camera_index}")
                self.is_camera_active = True
                self.update_camera()
            else:
                print("Error: Could not open any video stream.")
                self.camera_label.configure(text="Camera not available.\nCheck permissions or if it's in use.")
                self.is_camera_active = False

    def stop_camera(self):
        self.is_camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def update_camera(self):
        if not self.is_camera_active or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv.flip(frame, 1)
            
            if self.workout_in_progress:
                frame = self.process_frame(frame)
            
            frame = cv.resize(frame, (640, 480))
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 480))
            self.camera_label.configure(image=ctk_image, text="")
            
        else:
            self.camera_label.configure(image=None, text="Camera not available")
            
        self.root.after(10, self.update_camera)

    def process_frame(self, frame):
        with mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.65) as pose:
            image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                landmarks = results.pose_landmarks.landmark
                rep_detected = False
                exercise_angle = 0
                
                if self.current_exercise == "bicep_curl":
                    rep_detected, exercise_angle = self.bicep_curl_logic(landmarks)
                elif self.current_exercise == "shoulder_press":
                    rep_detected, exercise_angle = self.shoulder_press_logic(landmarks)
                elif self.current_exercise == "squat":
                    rep_detected, exercise_angle = self.squat_logic(landmarks)
                elif self.current_exercise == "push_up":
                    rep_detected, exercise_angle = self.push_up_logic(landmarks)
                elif self.current_exercise == "plank":
                    rep_detected, exercise_angle = self.plank_logic(landmarks)
                elif self.current_exercise == "stretch":
                    rep_detected, exercise_angle = self.stretch_logic(landmarks)
                
                if rep_detected:
                    self.counter += 1
                    self.reps_label.configure(text=f"{self.counter}/{self.selected_program['reps']}")
                    self.last_rep_time = time.time()
                    self.motivation_played = False
                    
                    if self.counter >= self.selected_program['reps']:
                        self.next_exercise_btn.configure(state="normal")
                        self.current_quote = "SET COMPLETE! TIME FOR A QUICK BREAK."
                        self.quote_display_time = time.time()
                
                cv.putText(image, f"Angle: {int(exercise_angle)}", (10, 90),
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv.putText(image, f"Exercise: {EXERCISES[self.current_exercise]['name']}", (10, 30),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv.putText(image, f"Set: {self.current_set}/{self.selected_program['sets']}", (10, 60),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            current_time = time.time()
            rest_duration = current_time - self.last_rep_time
            
            if rest_duration > self.LONG_REST_THRESHOLD and not self.motivation_played:
                self.current_quote = random.choice(MOTIVATIONAL_QUOTES)
                self.quote_display_time = time.time()
                self.motivation_played = True
                
            if current_time - self.quote_display_time < 3:
                cv.putText(image, self.current_quote, (100, 300),
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return image
        
        return frame
        
    # Exercise logic functions (remain unchanged)
    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle
        
    def bicep_curl_logic(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        angle = self.calculate_angle((shoulder.x, shoulder.y), (elbow.x, elbow.y), (wrist.x, wrist.y))
        if angle > 160:
            self.stage = "down"
        if angle < 50 and self.stage == 'down':
            self.stage = "up"
            return True, angle
        return False, angle
        
    def shoulder_press_logic(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        angle = self.calculate_angle((shoulder.x, shoulder.y), (elbow.x, elbow.y), (wrist.x, wrist.y))
        if angle < 60:
            self.stage = "down"
        if angle > 150 and self.stage == 'down':
            self.stage = "up"
            return True, angle
        return False, angle
        
    def squat_logic(self, landmarks):
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        angle = self.calculate_angle((hip.x, hip.y), (knee.x, knee.y), (ankle.x, ankle.y))
        if angle > 160:
            self.stage = "up"
        if angle < 100 and self.stage == 'up':
            self.stage = "down"
            return True, angle
        return False, angle
        
    def push_up_logic(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        angle = self.calculate_angle((shoulder.x, shoulder.y), (elbow.x, elbow.y), (wrist.x, wrist.y))
        if angle > 160:
            self.stage = "up"
        if angle < 90 and self.stage == 'up':
            self.stage = "down"
            return True, angle
        return False, angle
        
    def plank_logic(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        angle = self.calculate_angle((shoulder.x, shoulder.y), (hip.x, hip.y), (ankle.x, ankle.y))
        rep_detected = False
        if time.time() - self.last_rep_time > 3:
            rep_detected = True
        return rep_detected, angle
        
    def stretch_logic(self, landmarks):
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        angle = self.calculate_angle((shoulder.x, shoulder.y), (hip.x, hip.y), (ankle.x, ankle.y))
        if angle > 170:
            self.stage = "extended"
        if angle < 140 and self.stage == 'extended':
            self.stage = "bent"
            return True, angle
        return False, angle
        
    def run(self):
        self.root.mainloop()
        
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    app = FitnessApp()
    app.run()