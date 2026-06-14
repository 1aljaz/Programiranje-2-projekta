// Mirrors sf::Event. Only the fields the games actually use are kept.
public class Event {
    public enum Type { Closed, KeyPressed, MouseButtonPressed, MouseMoved, TextEntered }

    public Type type;
    public int code = -1;   // key code (KeyEvent.VK_*) for KeyPressed
    public char unicode;    // typed character for TextEntered
    public int x, y;        // mouse coordinates

    public static Event closed() {
        Event e = new Event();
        e.type = Type.Closed;
        return e;
    }

    public static Event keyPressed(int code) {
        Event e = new Event();
        e.type = Type.KeyPressed;
        e.code = code;
        return e;
    }

    public static Event mousePressed(int x, int y) {
        Event e = new Event();
        e.type = Type.MouseButtonPressed;
        e.x = x;
        e.y = y;
        return e;
    }

    public static Event mouseMoved(int x, int y) {
        Event e = new Event();
        e.type = Type.MouseMoved;
        e.x = x;
        e.y = y;
        return e;
    }

    public static Event textEntered(char unicode) {
        Event e = new Event();
        e.type = Type.TextEntered;
        e.unicode = unicode;
        return e;
    }
}
