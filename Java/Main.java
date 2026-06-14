import java.awt.Color;
import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;

public class Main {
    static int pagenum = 1000;
    static int game_selection;
    static BufferedImage background;

    static void imageload(GameMenu gamemenu) {
        switch (gamemenu.pressed()) {
            case 0:
                background = Assets.loadImage("assets/image/random2.jpg");
                break;
            case 1:
                background = Assets.loadImage("assets/image/random.jpg");
                break;
        }
    }

    static int selectGame(GameWindow mainmenu, GameMenu gamemenu) {
        imageload(gamemenu);
        while (mainmenu.isOpen()) {
            Event event;
            while ((event = mainmenu.pollEvent()) != null) {
                if (event.type == Event.Type.Closed) {
                    mainmenu.close();
                    break;
                }
                if (event.type == Event.Type.KeyPressed) {
                    if (event.code == KeyEvent.VK_RIGHT) {
                        gamemenu.MoveRight();
                    }
                    if (event.code == KeyEvent.VK_LEFT) {
                        gamemenu.MoveLeft();
                    }
                    if (event.code == KeyEvent.VK_ENTER) {
                        game_selection = gamemenu.pressed();
                        return game_selection;
                    }
                    if (event.code == KeyEvent.VK_ESCAPE) {
                        pagenum = 1000; // back to the main menu
                        return -1;
                    }
                    imageload(gamemenu);
                }
            }
            if (!mainmenu.isOpen())
                break;
            mainmenu.clear();
            drawBackground(mainmenu);
            gamemenu.draw(mainmenu);
            mainmenu.display();
            GameWindow.sleep(16);
        }
        return -1;
    }

    static void drawBackground(GameWindow window) {
        if (background != null) {
            window.getGraphics().drawImage(background, 0, 0, null);
        }
    }

    public static void main(String[] args) {
        GameWindow mainmenu = new GameWindow(1920, 1080, "Game", true);
        Menu menu = new Menu(1920, 1080);
        GameMenu gamemenu = new GameMenu(1920, 1080);
        background = Assets.loadImage("assets/image/background.jpg");

        boolean gameSelected = false; // Flag to track if a game has been selected
        boolean exitGame = false;     // Flag to track when to exit the main loop

        while (!exitGame) {
            if (pagenum == 1000) { // main menu if
                while (mainmenu.isOpen() && !exitGame) {
                    Event event;
                    while ((event = mainmenu.pollEvent()) != null) {
                        if (event.type == Event.Type.Closed) {
                            mainmenu.close();
                            exitGame = true; // Set the flag to exit the main loop
                            break;
                        }
                        if (event.type == Event.Type.KeyPressed) {
                            if (event.code == KeyEvent.VK_UP) {
                                menu.MoveUp();
                            }
                            if (event.code == KeyEvent.VK_DOWN) {
                                menu.MoveDown();
                            }
                            if (event.code == KeyEvent.VK_ENTER) {
                                if (menu.pressed() == 0)
                                    pagenum = 0;
                                else if (menu.pressed() == 1)
                                    pagenum = 1;
                                else if (menu.pressed() == 2)
                                    pagenum = -1;
                            }
                        }
                    }
                    if (pagenum != 1000)
                        break;
                    if (!mainmenu.isOpen() || exitGame)
                        break;

                    mainmenu.clear();
                    drawBackground(mainmenu);
                    menu.draw(mainmenu);
                    mainmenu.display();
                    GameWindow.sleep(16);
                }
                if (pagenum == -1) {
                    mainmenu.close();
                    break;
                }
                if (pagenum == 1) {
                    GameWindow window = new GameWindow(1920, 1080, "About");
                    java.awt.Font font = Assets.loadFont("assets/fonts/arial.ttf");

                    Text text = new Text();
                    text.setFont(font);
                    text.setString("Premik po glavnem zaslonu: puščice gor in dol na tipkovnici, tipka 'Enter' pa odpre meni\nZ klikom na Play boste poslani na meni iger, po njih se lahko premikate z puščicami levo in desno\nMaze runner upravljate z puščicami na tipkovnici\n\ns pritiskom na 'Escape' boste poslani ven iz igre,zaslona iger, ter menija za pomoč.");
                    text.setCharacterSize(24);
                    text.setPosition(100, 100);
                    text.setFillColor(Color.WHITE);

                    while (window.isOpen()) {
                        Event event;
                        while ((event = window.pollEvent()) != null) {
                            if (event.type == Event.Type.Closed || event.code == KeyEvent.VK_ESCAPE) {
                                window.close();
                                pagenum = 1000;
                            }
                        }
                        if (!window.isOpen())
                            break;
                        window.clear();
                        text.draw(window.getGraphics());
                        window.display();
                        GameWindow.sleep(16);
                    }
                }
            }
            if (pagenum == 0 && !gameSelected) {
                game_selection = selectGame(mainmenu, gamemenu);
                gameSelected = true;

                // Handle the selected game here
                switch (game_selection) {
                    case 0: {
                        Cell maze = new Cell();
                        pagenum = maze.Run();
                        gameSelected = false;
                        break;
                    }
                    case 1: {
                        PongGame pong = new PongGame();
                        pong.Run();
                        pagenum = 0;
                        gameSelected = false;
                        break;
                    }
                    default: // Escape/closed in the menu: no game launched
                        gameSelected = false;
                        break;
                }
            }

            // Safety: the selection window was closed (game_selection == -1)
            if (!mainmenu.isOpen())
                break;
        }
        System.exit(0);
    }
}
