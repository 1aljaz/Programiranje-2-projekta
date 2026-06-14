import java.awt.Color;
import java.awt.Font;

public class Menu {
    public Text[] mainmenu = new Text[3];
    private int selected;
    private Font font;

    public Menu(float width, float height) {
        font = Assets.loadFont("assets/fonts/Gatrich.otf");

        for (int i = 0; i < 3; i++) {
            mainmenu[i] = new Text();
        }
        // play
        mainmenu[0].setFont(font);
        mainmenu[0].setFillColor(Color.YELLOW);
        mainmenu[0].setString("Play");
        mainmenu[0].setCharacterSize(70);
        mainmenu[0].setPosition(150, 150);
        // options
        mainmenu[1].setFont(font);
        mainmenu[1].setFillColor(Color.WHITE);
        mainmenu[1].setString("Help");
        mainmenu[1].setCharacterSize(70);
        mainmenu[1].setPosition(150, 250);
        // Exit
        mainmenu[2].setFont(font);
        mainmenu[2].setFillColor(Color.WHITE);
        mainmenu[2].setString("Exit");
        mainmenu[2].setCharacterSize(70);
        mainmenu[2].setPosition(150, 350);

        selected = 0;
    }

    public int pressed() {
        return selected;
    }

    public void setSelected(int n) {
        selected = n;
    }

    public void draw(GameWindow window) {
        for (int i = 0; i < 3; i++) {
            mainmenu[i].draw(window.getGraphics());
        }
    }

    public void MoveDown() {
        mainmenu[selected].setFillColor(Color.WHITE);
        selected = (selected + 1) % 3;
        mainmenu[selected].setFillColor(Color.YELLOW);
    }

    public void MoveUp() {
        mainmenu[selected].setFillColor(Color.WHITE);
        selected = (selected + 2) % 3;
        mainmenu[selected].setFillColor(Color.YELLOW);
    }
}
