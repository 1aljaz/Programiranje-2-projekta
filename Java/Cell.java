import java.awt.Color;
import java.awt.Graphics2D;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Random;
import java.awt.event.KeyEvent;

public class Cell {
    public static final int SIZE = 30;
    public static final int CELL_WIDTH = 20;

    // One shared RNG instead of re-seeding a fresh generator on every cell.
    private static final Random rng = new Random();

    public int x, y;
    public int pos;
    public float size = 30f;
    public float thickness = 2f;
    public boolean[] walls = {true, true, true, true};
    public boolean visited = false;
    public boolean isActive = false;

    public Cell() {}

    public Cell(int _x, int _y) {
        x = _x;
        y = _y;
    }

    static void resetMaze(Cell[] maze, int size) {
        for (int i = 0; i < size * size; i++) {
            for (int j = 0; j < 4; j++) {
                maze[i].walls[j] = true;
            }
            maze[i].visited = false;
            maze[i].isActive = false;
        }
    }

    static void removeWallsBetween(Cell[] maze, Cell current, Cell chosen, int size) {
        // top
        if (current.pos - size == chosen.pos) {
            current.walls[0] = false;
            chosen.walls[2] = false;
            // right
        } else if (current.pos + 1 == chosen.pos) {
            current.walls[1] = false;
            chosen.walls[3] = false;
            // bottom
        } else if (current.pos + size == chosen.pos) {
            current.walls[2] = false;
            chosen.walls[0] = false;
            // left
        } else if (current.pos - 1 == chosen.pos) {
            current.walls[3] = false;
            chosen.walls[1] = false;
        }
    }

    static void makeMaze(Cell[] maze, int size) {
        resetMaze(maze, size);
        Deque<Cell> stack = new ArrayDeque<>();
        maze[0].visited = true;
        stack.push(maze[0]);

        while (!stack.isEmpty()) {
            Cell current = stack.pop();
            int pos = current.pos;
            List<Integer> neighbours = new ArrayList<>();

            if ((pos) % (size) != 0 && pos > 0) {
                Cell left = maze[pos - 1];
                if (!left.visited) {
                    neighbours.add(pos - 1);
                }
            }
            if ((pos + 1) % (size) != 0 && pos < size * size) {
                Cell right = maze[pos + 1];
                if (!right.visited) {
                    neighbours.add(pos + 1);
                }
            }
            if ((pos + size) < size * size) {
                Cell bottom = maze[pos + size];
                if (!bottom.visited) {
                    neighbours.add(pos + size);
                }
            }
            if ((pos - size) > 0) {
                Cell top = maze[pos - size];
                if (!top.visited) {
                    neighbours.add(pos - size);
                }
            }

            if (neighbours.size() > 0) {
                int randneighbourpos = rng.nextInt(neighbours.size());
                Cell chosen = maze[neighbours.get(randneighbourpos)];

                stack.push(current);
                removeWallsBetween(maze, maze[current.pos], chosen, size);

                chosen.visited = true;
                stack.push(chosen);
            }
        }
    }

    static void handleMove(Event event, Cell[] maze, int[] currentPos, int size) {
        if (event.code == KeyEvent.VK_LEFT || event.code == KeyEvent.VK_H) {
            if (!maze[currentPos[0]].walls[3] && !maze[currentPos[0] - 1].walls[1]) {
                currentPos[0] = currentPos[0] - 1;
                maze[currentPos[0]].isActive = true;
            }
        } else if (event.code == KeyEvent.VK_RIGHT || event.code == KeyEvent.VK_L) {
            if (!maze[currentPos[0]].walls[1] && !maze[currentPos[0] + 1].walls[3]) {
                currentPos[0] = currentPos[0] + 1;
                maze[currentPos[0]].isActive = true;
            }
        } else if (event.code == KeyEvent.VK_UP || event.code == KeyEvent.VK_K) {
            if ((currentPos[0] - size) < 0) {
                return;
            }
            if (!maze[currentPos[0]].walls[0] && !maze[currentPos[0] - size].walls[2]) {
                currentPos[0] = currentPos[0] - size;
                maze[currentPos[0]].isActive = true;
            }
        } else if (event.code == KeyEvent.VK_DOWN || event.code == KeyEvent.VK_J) {
            if ((currentPos[0] + size) > size * size) {
                return;
            }
            if (!maze[currentPos[0]].walls[2] && !maze[currentPos[0] + size].walls[0]) {
                currentPos[0] = currentPos[0] + size;
                maze[currentPos[0]].isActive = true;
            }
        }
    }

    public void draw(GameWindow window) {
        Graphics2D g = window.getGraphics();

        if (isActive) {
            g.setColor(new Color(247, 23, 53));
            g.fillRect(x, y, (int) size, (int) size);
        }
        g.setColor(new Color(223, 243, 228));

        if (walls[0]) {
            g.fillRect(x, y, (int) size, (int) thickness);
        }
        // right
        if (walls[1]) {
            g.fillRect(x + (int) size, y, (int) thickness, (int) size);
        }
        // bottom
        if (walls[2]) {
            g.fillRect(x, y + (int) size, (int) (size + thickness), (int) thickness);
        }
        // left
        if (walls[3]) {
            g.fillRect(x, y, (int) thickness, (int) size);
        }
    }

    public int Run() {
        int[] currentPos = {0};

        GameWindow window = new GameWindow(CELL_WIDTH * SIZE + 60, CELL_WIDTH * SIZE + 60, "maze");
        Cell[] maze = new Cell[SIZE * SIZE];
        for (int i = 0; i < maze.length; i++) maze[i] = new Cell();

        for (int i = 30, k = 0; i < CELL_WIDTH * SIZE + 30; i += CELL_WIDTH) {
            for (int j = 30; j < CELL_WIDTH * SIZE + 30; j += CELL_WIDTH, k++) {
                maze[k].y = i;
                maze[k].x = j;
                maze[k].size = CELL_WIDTH;
                maze[k].pos = k;
            }
        }

        makeMaze(maze, SIZE);
        maze[currentPos[0]].isActive = true;

        while (window.isOpen()) {
            Event event;
            while ((event = window.pollEvent()) != null) {
                switch (event.type) {
                    case Closed:
                        window.close();
                        break;
                    case KeyPressed:
                        handleMove(event, maze, currentPos, SIZE);
                        if (event.code == KeyEvent.VK_ESCAPE) {
                            window.close();
                            return 0;
                        }
                        break;
                    default:
                        break;
                }
            }

            if (!window.isOpen())
                break;

            if (currentPos[0] == (SIZE * SIZE - 1)) {
                makeMaze(maze, SIZE);
                currentPos[0] = 0;
                maze[currentPos[0]].isActive = true;
            }

            window.clear(new Color(13, 2, 33));

            for (int i = 0; i < SIZE * SIZE; i++) {
                maze[i].draw(window);
            }

            Graphics2D g = window.getGraphics();
            g.setColor(new Color(166, 207, 213));
            g.fillRect(maze[currentPos[0]].x, maze[currentPos[0]].y, CELL_WIDTH, CELL_WIDTH);
            g.setColor(new Color(0, 128, 0));
            g.fillRect(maze[SIZE * SIZE - 1].x, maze[SIZE * SIZE - 1].y, CELL_WIDTH, CELL_WIDTH);

            window.display();
            GameWindow.sleep(33); // ~30 FPS
        }
        return 0;
    }
}
