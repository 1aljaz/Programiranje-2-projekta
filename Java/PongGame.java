import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.event.KeyEvent;
import java.awt.geom.Rectangle2D;

public class PongGame {
    public boolean isFirstBounce;

    private GameWindow window;
    private Rect paddle1;
    private Rect paddle2;
    private Circle ball;

    private float ballSpeedX;
    private float ballSpeedY;
    private float ballSpeed; // ramp multiplier that grows the longer a rally lasts

    private int leftScore;
    private int rightScore;

    private final Font font;

    private static class Rect {
        float x, y, w, h;
        Rect(float w, float h) { this.w = w; this.h = h; }
        void setPosition(float x, float y) { this.x = x; this.y = y; }
        void move(float dx, float dy) { x += dx; y += dy; }
        boolean intersects(Rect o) {
            return x < o.x + o.w && x + w > o.x && y < o.y + o.h && y + h > o.y;
        }
    }

    private static class Circle {
        float x, y, r;
        Circle(float r) { this.r = r; }
        void setPosition(float x, float y) { this.x = x; this.y = y; }
        void move(float dx, float dy) { x += dx; y += dy; }
        Rect bounds() {
            Rect b = new Rect(r * 2, r * 2);
            b.setPosition(x, y);
            return b;
        }
    }

    public PongGame() {
        window = new GameWindow(800, 600, "Pong Game");
        paddle1 = new Rect(20, 100);
        paddle2 = new Rect(20, 100);
        ball = new Circle(10);
        ballSpeedX = -2.0f;
        ballSpeedY = 1.0f;
        ballSpeed = 1.0f;
        leftScore = 0;
        rightScore = 0;
        isFirstBounce = true;

        // Loaded once here instead of on every render frame.
        font = Assets.loadFont("assets/fonts/arial.ttf");

        paddle1.setPosition(50, 250);
        paddle2.setPosition(730, 250);
        ball.setPosition(400, 300);
    }

    public void Run() {
        GameWindow.sleep(1000);

        while (window.isOpen()) {
            processEvents();
            if (!window.isOpen())
                break;
            update();
            render();
            GameWindow.sleep(16);
        }
    }

    private void processEvents() {
        Event event;
        while ((event = window.pollEvent()) != null) {
            if (event.type == Event.Type.Closed)
                window.close();
            if (event.code == KeyEvent.VK_ESCAPE) {
                window.close();
            }
        }

        // Paddles also speed up over time, but less drastically than the ball.
        float paddleSpeed = 2.5f * (1f + (ballSpeed - 1f) * 0.25f);

        if (window.isKeyPressed(KeyEvent.VK_W) && paddle1.y > 0)
            paddle1.move(0, -paddleSpeed);

        if (window.isKeyPressed(KeyEvent.VK_S) && paddle1.y + paddle1.h < window.getHeight())
            paddle1.move(0, paddleSpeed);

        if (window.isKeyPressed(KeyEvent.VK_UP) && paddle2.y > 0)
            paddle2.move(0, -paddleSpeed);

        if (window.isKeyPressed(KeyEvent.VK_DOWN) && paddle2.y + paddle2.h < window.getHeight())
            paddle2.move(0, paddleSpeed);
    }

    private void update() {
        // The ball speeds up the longer the rally goes on (reset on each point).
        if (ballSpeed < 3.0f) ballSpeed += 0.005f;
        ball.move(ballSpeedX * ballSpeed, ballSpeedY * ballSpeed);

        if (ball.y < 0 || ball.y + ball.r * 2 > window.getHeight()) {
            ballSpeedY = -ballSpeedY;
        }

        // Only reverse when the ball is actually heading into the paddle, so it
        // can't stick by reversing every frame while still overlapping it.
        boolean hitLeft = ball.bounds().intersects(paddle1) && ballSpeedX < 0;
        boolean hitRight = ball.bounds().intersects(paddle2) && ballSpeedX > 0;
        if (hitLeft || hitRight) {
            ballSpeedX = -ballSpeedX;
            if (isFirstBounce) {
                // keep the new (away-from-paddle) direction; bias toward the x-axis
                ballSpeedX = ballSpeedX < 0 ? -2.0f : 2.0f;
                ballSpeedY = 1;
                isFirstBounce = false;
            }
        }
        if (ball.x + ball.r * 2 < 0) {
            ++rightScore;
            ball.setPosition(400, 300);
            GameWindow.sleep(1000);
            ballSpeedX = 2;
            ballSpeedY = 1;
            isFirstBounce = true;
            ballSpeed = 1.0f;
        } else if (ball.x > window.getWidth()) {
            ++leftScore;
            ball.setPosition(400, 300);
            GameWindow.sleep(1000);
            ballSpeedX = 2;
            ballSpeedY = 1;
            isFirstBounce = true;
            ballSpeed = 1.0f;
        }
    }

    private void render() {
        window.clear();
        Graphics2D g = window.getGraphics();

        g.setColor(Color.WHITE);
        g.fillRect((int) paddle1.x, (int) paddle1.y, (int) paddle1.w, (int) paddle1.h);
        g.fillRect((int) paddle2.x, (int) paddle2.y, (int) paddle2.w, (int) paddle2.h);
        g.fillOval((int) ball.x, (int) ball.y, (int) (ball.r * 2), (int) (ball.r * 2));

        Text leftScoreText = new Text();
        leftScoreText.setFont(font);
        leftScoreText.setString("Left Player: " + leftScore);
        leftScoreText.setCharacterSize(24);
        leftScoreText.setFillColor(Color.WHITE);
        leftScoreText.setPosition(20, 20);
        leftScoreText.draw(g);

        Text rightScoreText = new Text();
        rightScoreText.setFont(font);
        rightScoreText.setString("Right Player: " + rightScore);
        rightScoreText.setCharacterSize(24);
        rightScoreText.setFillColor(Color.WHITE);
        Rectangle2D rb = rightScoreText.getGlobalBounds();
        rightScoreText.setPosition(window.getWidth() - (float) rb.getWidth() - 20, 20);
        rightScoreText.draw(g);

        Text controlText = new Text();
        controlText.setFont(font);
        controlText.setString("Controls:\nLeft Player: W/S\nRight Player: Up/Down");
        controlText.setCharacterSize(24);
        controlText.setFillColor(Color.WHITE);
        Rectangle2D cb = controlText.getGlobalBounds();
        controlText.setPosition(window.getWidth() / 2f - (float) cb.getWidth() / 2f, 0);
        controlText.draw(g);

        window.display();
    }
}
