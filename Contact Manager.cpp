#include <iostream>
#include <vector>
#include <string>
#include <set>
#include <unordered_map>
#include <chrono>
#include <limits>
#include <algorithm>
#include <fstream>
using namespace std;
using namespace chrono;

struct Contact {
    string name;
    string ph;
    void display() {
        cout << "Name: " << name << "\nContact number: " << ph << "\n";
    }
};

class ContactManager {
private:
    vector<Contact> v;
    unordered_map<string, int> talk_time;
    set<string> fav;
    vector<string> recent;

    // Converts a string to lowercase (useful for case-insensitive search)
string inlowercase(string s) {
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

// Save a new contact to the file
void saveContactToFile(const Contact& c) {
    ofstream outFile("contacts.txt", ios::app);
    outFile << c.name << "," << c.ph << "\n";
    outFile.close();
}

// Save all talk durations to file
void saveTalkTime() {
    ofstream out("talk_time.txt");
    for (auto& pair : talk_time)
        out << pair.first << "," << pair.second << "\n";
    out.close();
}

// Save all favourite contacts to file
void saveFavourites() {
    ofstream out("favourites.txt");
    for (auto& name : fav)
        out << name << "\n";
    out.close();
}

// Save recent contacts to file
void saveRecent() {
    ofstream out("recent.txt");
    for (auto& name : recent)
        out << name << "\n";
    out.close();
}

// Load contacts from file (on app start)
void loadContactsFromFile() {
    ifstream inFile("contacts.txt");
    string line;
    while (getline(inFile, line)) {
        size_t commaPos = line.find(',');
        if (commaPos != string::npos) {
            Contact c;
            c.name = line.substr(0, commaPos);
            c.ph = line.substr(commaPos + 1);
            v.push_back(c);
        }
    }
    inFile.close();
}

// Load all talk durations from file
void loadTalkTime() {
    ifstream in("talk_time.txt");
    string line;
    while (getline(in, line)) {
        size_t pos = line.find(',');
        if (pos != string::npos) {
            string name = line.substr(0, pos);
            int time = stoi(line.substr(pos + 1));
            talk_time[name] = time;
        }
    }
    in.close();
}

// Load favourites from file
void loadFavourites() {
    ifstream in("favourites.txt");
    string name;
    while (getline(in, name)) {
        fav.insert(name);
    }
    in.close();
}

// Load recent contacts from file
void loadRecent() {
    ifstream in("recent.txt");
    string name;
    while (getline(in, name)) {
        recent.push_back(name);
    }
    in.close();
}
public :
// Add a new contact
void addContact() {
    Contact c;
    cout << "Enter name: ";
    cin.ignore();
    getline(cin, c.name);
    cout << "Enter phone number: ";
    getline(cin, c.ph);
    v.push_back(c);
    saveContactToFile(c);
    cout << "Contact saved.\n";
}

// Simulate a phone call with time tracking
void simulate_call(string contact) {
    cout << "\nPress Enter to start the call with " << contact << "...";
    cin.ignore();
    auto start = high_resolution_clock::now();
    cout << "Call started. Press Enter again to end the call...";
    cin.ignore();
    auto end = high_resolution_clock::now();
    int duration = duration_cast<seconds>(end - start).count();
    talk_time[contact] += duration;
    saveTalkTime();
    recent.push_back(contact);
    saveRecent();
    cout << "Call with " << contact << " ended. Duration: " << duration << " seconds\n";
    if (duration > 600) {
        char choice;
        cout << "Long call detected! Add " << contact << " to favourites? (y/n): ";
        cin >> choice;
        if (choice == 'y' || choice == 'Y') {
            fav.insert(contact);
            saveFavourites();
            cout << contact << " added to favourites.\n";
        }
        cin.ignore();
    }
}

// Show the contact you talked to the most
void mostTalked() {
    if (talk_time.empty()) {
        cout << "No calls made yet.\n";
        return;
    }
    string top;
    int maxtime = 0;
    for (auto& pair : talk_time) {
        if (pair.second > maxtime) {
            maxtime = pair.second;
            top = pair.first;
        }
    }
    cout << "Most talked contact: " << top << " (" << maxtime << " seconds)\n";
}

// Display favourite contacts
void showFavourites() {
    if (fav.empty()) {
        cout << "No favourites yet.\n";
    } else {
        for (const auto& contact : fav)
            cout << "- " << contact << "\n";
    }
}

// Search a contact by name (case-insensitive)
void searchContact() {
    cout << "Enter name to search: ";
    string name;
    char choice;
    cin.ignore();
    getline(cin, name);
    string lower_name = inlowercase(name);
    bool found = false;
    for (auto& c : v) {
        if (inlowercase(c.name) == lower_name) {
            c.display();
            found = true;
            recent.push_back(c.name);
            saveRecent();
            break;
        }
    }
    if (!found) {
        cout << "Contact not found.\n";
        cout << "\nDid you mean:\n";
        for (auto& c : v) {
            if (inlowercase(c.name).find(lower_name) != string::npos) {
                cout << "- " << c.name << "\n";
                cout << "Want to call " << c.name << "? (y/n): ";
                cin >> choice;
                if (choice == 'y' || choice == 'Y') {
                    simulate_call(c.name);
                } else {
                    cout << "Consider retyping the contact.\n";
                }
            }
        }
    }
}

// Show the last contacted person
void recentlyContacted() {
    if (recent.empty()) {
        cout << "No recent contacts.\n";
    } else
        cout << recent.back() << "\n"; }
};

int main() {
    int choice;
    string cname;
    ContactManager cm;
    while (true) {
        cout << "\n1. Add Contact\n2. Search Contact\n3. Start Call\n4. Most Talked Contact\n5. Show Favourites\n6. Recently Contacted\n7. Exit\n";
        cout << "Enter choice: ";
        cin >> choice;
        switch (choice) {
            case 1:
                cm.addContact();
                break;
            case 2:
                cm.searchContact();
                break;
            case 3:
                cout << "Enter name to call: ";
                cin.ignore();
                getline(cin, cname);
                cm.simulate_call(cname);
                break;
            case 4:
                cm.mostTalked();
                break;
            case 5:
                cm.showFavourites();
                break;
            case 6:
                cm.recentlyContacted();
                break;
            case 7:
                return 0;
            default:
                cout << "Invalid choice.\n";
        }
    }
}
    