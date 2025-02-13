from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class WiiMenuApp(App):
    def build(self):
        # Create a grid layout with 3 columns
        layout = GridLayout(cols=3, padding=10, spacing=10)
        
        # Add 9 dummy game buttons (you can change the number as needed)
        for i in range(9):
            btn = Button(text=f'Game {i+1}', font_size=24)
            btn.bind(on_press=self.on_button_press)
            layout.add_widget(btn)
        
        return layout

    def on_button_press(self, instance):
        # This function will be called when a button is pressed
        print(f'You pressed: {instance.text}')

if __name__ == '__main__':
    WiiMenuApp().run()

