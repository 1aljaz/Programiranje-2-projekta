import java.awt.Font;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

public class Assets {
    public static Font loadFont(String path) {
        try {
            return Font.createFont(Font.TRUETYPE_FONT, new File(path));
        } catch (Exception e) {
            System.err.println("font loading error");
            return new Font("SansSerif", Font.PLAIN, 12);
        }
    }

    public static BufferedImage loadImage(String path) {
        try {
            return ImageIO.read(new File(path));
        } catch (Exception e) {
            System.err.println("image loading error: " + path);
            return null;
        }
    }
}
