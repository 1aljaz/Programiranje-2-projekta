import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;

public class Text {
    private static final Graphics2D SCRATCH =
        new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB).createGraphics();

    private Font font = new Font("SansSerif", Font.PLAIN, 12);
    private Color color = Color.WHITE;
    private String string = "";
    private int characterSize = 30;
    private float x, y;

    public void setFont(Font font) {
        this.font = font;
    }

    public void setFillColor(Color color) {
        this.color = color;
    }

    public void setString(String string) {
        this.string = string;
    }

    public String getString() {
        return string;
    }

    public void setCharacterSize(int characterSize) {
        this.characterSize = characterSize;
    }

    public void setPosition(float x, float y) {
        this.x = x;
        this.y = y;
    }

    private Font sizedFont() {
        return font.deriveFont((float) characterSize);
    }

    public Rectangle2D getLocalBounds() {
        FontMetrics fm = SCRATCH.getFontMetrics(sizedFont());
        String[] lines = string.split("\n", -1);
        int w = 0;
        for (String line : lines) {
            w = Math.max(w, fm.stringWidth(line));
        }
        return new Rectangle2D.Float(0, 0, w, (float) fm.getHeight() * lines.length);
    }

    public Rectangle2D getGlobalBounds() {
        return getLocalBounds();
    }

    public void draw(Graphics2D g) {
        Font sized = sizedFont();
        g.setFont(sized);
        g.setColor(color);
        FontMetrics fm = g.getFontMetrics(sized);
        int baseline = (int) y + fm.getAscent();
        for (String line : string.split("\n", -1)) {
            g.drawString(line, x, baseline);
            baseline += fm.getHeight();
        }
    }
}
