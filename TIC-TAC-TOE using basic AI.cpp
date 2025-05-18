#include <iostream>
#include <cstdlib>
#include <ctime>
using namespace std;

// ANSI color codes
const string GREEN = "\033[32m";
const string RED = "\033[31m";
const string GRAY = "\033[90m";
const string RESET = "\033[0m";

// Function to print the board with colors
void print(char arr[]) {
    for (int i = 0; i < 9; i++) {
        if (arr[i] == 'X')
            cout << GREEN << arr[i] << RESET << " ";
        else if (arr[i] == 'O')
            cout << RED << arr[i] << RESET << " ";
        else
            cout << GRAY << arr[i] << RESET << " ";

        if ((i + 1) % 3 == 0)
            cout << "\n";
    }
}

// ... rest of your original code unchanged ...

bool result(char arr[], char player) {
    for (int i = 0; i < 9; i += 3)
        if (arr[i] == player && arr[i + 1] == player && arr[i + 2] == player)
            return true;
    for (int i = 0; i < 3; i++)
        if (arr[i] == player && arr[i + 3] == player && arr[i + 6] == player)
            return true;
    if (arr[0] == player && arr[4] == player && arr[8] == player)
        return true;
    if (arr[2] == player && arr[4] == player && arr[6] == player)
        return true;
    return false;
}

int findWinningMove(char arr[], char aiChar) {
    for (int i = 0; i < 9; ++i) {
        if (arr[i] == '.') {
            arr[i] = aiChar;
            if (result(arr, aiChar)) {
                arr[i] = '.';
                return i;
            }
            arr[i] = '.';
        }
    }
    return -1;
}

void loop(int *p, int *q, int y, int o) {
    int i, n, k, j, c = 0, turn1;
    char arr[] = {'.', '.', '.', '.', '.', '.', '.', '.', '.'};
    int a[9] = {0};
    srand(time(0));

    for (i = 1; i < 5; i++) {
        k = a[i];
        j = i - 1;
        while (j >= 0 && a[j] > k) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = k;
    }

    cout << "Round " << y << " out of " << o << "\n";
    for (i = 1; i <= 9; i++) {
        if (i % 2 != 0) {
            cout << "Place your 'X' at a position: ";
            cin >> n;
            while (n < 1 || n > 9 || arr[n - 1] != '.') {
                cout << "Invalid move. Try again: ";
                cin >> n;
            }
            a[c] = n;
            arr[n - 1] = 'X';
            c++;
        } else {
            cout << "Computer's turn: \n";
            if (i == 2) {
                do {
                    turn1 = rand() % 9;
                } while (arr[turn1] != '.');
                arr[turn1] = 'O';
            } else {
                int winMove = findWinningMove(arr, 'O');
                if (winMove != -1) {
                    arr[winMove] = 'O';
                } else {
                    int move = 2 * a[i - 3] - a[i - 4];
                    if (move >= 1 && move <= 9 && arr[move - 1] == '.')
                        arr[move - 1] = 'O';
                    else {
                        do {
                            turn1 = rand() % 9;
                        } while (arr[turn1] != '.');
                        arr[turn1] = 'O';
                    }
                }
            }
        }

        system("CLS"); // or system("clear"); for Linux/Mac
        print(arr);

        if (result(arr, 'X')) {
            cout << "Player wins!\n";
            (*p)++;
            break;
        }
        if (result(arr, 'O')) {
            cout << "AI wins!\n";
            (*q)++;
            break;
        }
        if (i == 9)
            cout << "It's a draw!\n";
    }
}

int main() {
    int i, o, p = 0, q = 0;
    cout << "Enter number of tournaments to be held:  ";
    cin >> o;

    for (i = 0; i < o; i++)
        loop(&p, &q, i + 1, o);

    if (p > q)
        cout << "You Won the tournament by " << p << " wins!";
    else if (p == q)
        cout << "Draw!";
    else
        cout << "Computer won the tournament by " << q << " wins!";
}
