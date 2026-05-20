import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "cli":
            from menus.menu_principal import menu_principal
            menu_principal()
        elif mode == "simple":
            from ui_simple import launch_simple_app
            launch_simple_app()
        else:
            print("Modo desconocido. Use 'cli' o 'simple'.")
    else:
        from ui_simple import launch_simple_app
        launch_simple_app()
