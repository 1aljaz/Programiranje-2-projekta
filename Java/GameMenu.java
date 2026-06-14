import java.awt.Color;
import java.awt.Font;

public class GameMenu {
    public Text[] selectionmenu = new Text[4];
    private int selected;
    private Font font;
    private Font font2;

    public GameMenu(float width, float height) {
        font = Assets.loadFont("assets/fonts/Gatrich.otf");
        font2 = Assets.loadFont("assets/fonts/arial.ttf");

        for (int i = 0; i < 4; i++) {
            selectionmenu[i] = new Text();
        }
        // game1
        selectionmenu[0].setFont(font);
        selectionmenu[0].setFillColor(Color.BLACK);
        selectionmenu[0].setString("Maze Runner");
        selectionmenu[0].setCharacterSize(40);
        selectionmenu[0].setPosition(145, 310);
        // game2
        selectionmenu[1].setFont(font);
        selectionmenu[1].setFillColor(Color.WHITE);
        selectionmenu[1].setString("Pong");
        selectionmenu[1].setCharacterSize(40);
        selectionmenu[1].setPosition(500, 310);
        // info
        selectionmenu[2].setFont(font2);
        selectionmenu[2].setFillColor(Color.WHITE);
        selectionmenu[2].setString("When in game press escape or close the window to come back to this menu");
        selectionmenu[2].setCharacterSize(40);
        selectionmenu[2].setPosition(250, 900);
        // title
        selectionmenu[3].setFont(font);
        selectionmenu[3].setFillColor(Color.WHITE);
        selectionmenu[3].setString("Pick a path");
        selectionmenu[3].setCharacterSize(70);
        selectionmenu[3].setPosition(120, 120);

        selected = 0;
    }

    public int pressed() {
        return selected;
    }

    public void setSelected(int n) {
        selected = n;
    }

    public void draw(GameWindow window) {
        for (int i = 0; i < 4; i++) {
            selectionmenu[i].draw(window.getGraphics());
        }
    }

    public void MoveRight() {
        selectionmenu[selected].setFillColor(Color.WHITE);
        selected = (selected + 1) % 2;
        selectionmenu[selected].setFillColor(Color.BLACK);
    }

    public void MoveLeft() {
        selectionmenu[selected].setFillColor(Color.WHITE);
        selected = (selected + 1) % 2;
        selectionmenu[selected].setFillColor(Color.BLACK);
    }
}
