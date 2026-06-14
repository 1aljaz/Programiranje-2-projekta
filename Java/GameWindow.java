import java.awt.Canvas;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Toolkit;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferStrategy;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import javax.swing.JFrame;

public class GameWindow {
    private final JFrame frame;
    private final Canvas canvas;
    private final BufferStrategy strategy;
    private final int width, height;

    private volatile boolean open = true;
    private final ConcurrentLinkedQueue<Event> events = new ConcurrentLinkedQueue<>();
    private final Set<Integer> keysDown = ConcurrentHashMap.newKeySet();
    private volatile int mouseX, mouseY;
    private Graphics2D g; 

    public GameWindow(int width, int height, String title) {
        this(width, height, title, false);
    }

    public GameWindow(int width, int height, String title, boolean fullscreen) {
        if (fullscreen) {
            // Borderless windowed fullscreen
            Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
            this.width = screen.width;
            this.height = screen.height;
        } else {
            this.width = width;
            this.height = height;
        }

        canvas = new Canvas();
        canvas.setPreferredSize(new Dimension(this.width, this.height));
        canvas.setFocusable(true);

        frame = new JFrame(title);
        frame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        frame.setResizable(false);
        frame.setUndecorated(fullscreen);
        frame.add(canvas);
        if (fullscreen) {
            frame.setBounds(0, 0, this.width, this.height);
            frame.setVisible(true);
        } else {
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        }

        frame.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                events.add(Event.closed());
            }
            public void windowActivated(WindowEvent e) {
                // Reclaim keyboard focus when this window comes to the front
                canvas.requestFocus();
            }
        });
        canvas.addKeyListener(new KeyAdapter() {
            public void keyPressed(KeyEvent e) {
                keysDown.add(e.getKeyCode());
                events.add(Event.keyPressed(e.getKeyCode()));
            }
            public void keyReleased(KeyEvent e) {
                keysDown.remove(e.getKeyCode());
            }
            public void keyTyped(KeyEvent e) {
                events.add(Event.textEntered(e.getKeyChar()));
            }
        });
        MouseAdapter mouse = new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                mouseX = e.getX();
                mouseY = e.getY();
                events.add(Event.mousePressed(e.getX(), e.getY()));
            }
            public void mouseMoved(MouseEvent e) {
                mouseX = e.getX();
                mouseY = e.getY();
                events.add(Event.mouseMoved(e.getX(), e.getY()));
            }
            public void mouseDragged(MouseEvent e) {
                mouseX = e.getX();
                mouseY = e.getY();
                events.add(Event.mouseMoved(e.getX(), e.getY()));
            }
        };
        canvas.addMouseListener(mouse);
        canvas.addMouseMotionListener(mouse);

        canvas.createBufferStrategy(2);
        strategy = canvas.getBufferStrategy();
        canvas.requestFocus();
    }

    public boolean isOpen() {
        return open;
    }

    public void close() {
        open = false;
        frame.dispose();
    }

    // Returns the next queued event, or null when the queue is empty
    public Event pollEvent() {
        return events.poll();
    }

    public boolean isKeyPressed(int keyCode) {
        return keysDown.contains(keyCode);
    }

    public int mouseX() {
        return mouseX;
    }

    public int mouseY() {
        return mouseY;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public void clear() {
        clear(Color.BLACK);
    }

    public void clear(Color color) {
        g = (Graphics2D) strategy.getDrawGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setColor(color);
        g.fillRect(0, 0, width, height);
    }

    // The drawing surface for the current frame (between clear() and display()).
    public Graphics2D getGraphics() {
        return g;
    }

    public void display() {
        g.dispose();
        if (!strategy.contentsLost()) {
            strategy.show();
        }
        Toolkit.getDefaultToolkit().sync();
    }

    public static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
