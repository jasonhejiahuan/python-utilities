
# Python Utilities

A collection of small utility programs that I built while learning Python. These are just for fun, but I hope they can help you with your tasks! Each script serves a unique purpose, from automating tasks to handling images and security.

## Utilities Overview

### 1. **CIE AUTO Check Score V5**

This script automates the process of checking the CIE (Color Index Evaluation) scores using a web interface. It utilizes `selenium` to interact with web elements in a Chrome browser, allowing for automated color score checks.

#### Features:
- **Secure Login**: Encrypts the username and password using XOR encryption combined with multi-layered Base64 encoding, storing them in an `.env` file.
- **Automated Result Checking**: Automatically checks the exam results page and refreshes periodically until the results are available.
- **Logging**: Logs the time when results are successfully retrieved.

#### Requirements:
- `selenium`
- `webdriver-manager`
- `python-dotenv`

#### Installation:
1. Clone the repository:

   ```bash
   git clone https://github.com/jasonhejiahuan/python-utilities.git
   cd python-utilities
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory of the project and add your credentials:

   ```env
   GLOBAL_ENCODED_CIE_USERNAME=your_encoded_username
   GLOBAL_ENCODED_CIE_PASSWORD=your_encoded_password
   ```

   You can generate these encoded credentials by running the script and following the prompts.

#### Usage:
To run the script, simply execute it:

```bash
python CIE\ AUTO\ Check\ Score\ V5.py
```

The script will handle the rest: encrypt your credentials, log in, and check your exam results periodically.

---

### 2. **PlusPhoto Downloader v7**

This script is designed to automate the downloading of photos from a live photo album. It uses Selenium to navigate through a webpage, extract image URLs, and download the images concurrently for efficient processing.

#### Features:
- **Web Scraping**: Automatically fetches images from a live photo album by interacting with the webpage using Selenium.
- **Logging**: Provides detailed logging of each step, including errors and successful downloads.
- **Concurrency**: Downloads multiple images concurrently using Python's `concurrent.futures` for faster processing.
- **Scrolling for Dynamic Content**: Automatically scrolls through the page to load more images, if necessary.
- **Image Downloading**: Downloads the original image in various formats (e.g., JPG, PNG) and saves them to a specified folder.

#### Requirements:
- `selenium`
- `webdriver-manager`
- `requests`
- `logging`
- `tqdm`

#### Installation:
1. Clone the repository:

   ```bash
   git clone https://github.com/jasonhejiahuan/python-utilities.git
   cd python-utilities
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Modify the script by specifying the target URL where your photo album is located:

   ```python
   TARGET_URL = 'YOUR_TARGET_URL_HERE'
   ```

#### Usage:
To run the script, simply execute it:

```bash
python PlusPhotoDownloader_v7.py
```

You will be prompted to input the photo album URL and other required details. The script will download the images to your specified folder.

---

### 3. **Image Download Test**

This script allows you to download one or multiple images from a URL. It includes features for both single image and batch image downloading, with support for dynamic generation of filenames and validation of the downloaded images.

#### Features:
- **Single Image Download**: Allows users to input a URL for a single image and download it, saving the image with its original filename.
- **Batch Image Download**: Allows users to specify a range of image filenames and download multiple images at once. 
- **File Hash Checking**: Ensures the integrity of the downloaded script by comparing the MD5 hash with the online version.
- **Automatic Script Update**: If a newer version of the script is available, it automatically updates itself.
- **Logging**: Tracks the download progress using a progress bar and logs image details like size, format, and resolution.
- **Image Validation**: Deletes any image files that are smaller than 5KB, assuming they're invalid.

#### Requirements:
- `requests`
- `Pillow`
- `matplotlib`
- `tqdm`

#### Installation:
1. Clone the repository:

   ```bash
   git clone https://github.com/jasonhejiahuan/python-utilities.git
   cd python-utilities
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

#### Usage:
To run the script, simply execute it:

```bash
python image_download_test.py
```

You will be prompted to choose one of the two download modes:

- **Mode 1**: Download a single image. Enter the image URL and it will be saved with its original filename.
- **Mode 2**: Download multiple images. Enter the base URL, file name range, and image format, and the script will download all images in the specified range.

After downloading, the script will display information about the images, including their dimensions, file size, and format. It will also clean up any invalid images (below 5KB in size).

---

### 4. **Safe Password Generator v2.0**

This script provides a secure way to encrypt and decrypt passwords using the Fernet encryption algorithm. It allows users to store encrypted passwords along with a key and retrieve them later using a password hint.

#### Features:
- **Password Encryption**: Encrypts passwords using a hint to generate a key. The password is encrypted with the Fernet algorithm, and the key is stored in a separate file for future use.
- **Password Decryption**: Allows users to decrypt the stored password by providing the correct hint and the key file.
- **Key and Password File**: Saves the encryption key and encrypted password in separate files, so the key can be used later to decrypt the password.
- **Error Handling**: Provides error messages in case the wrong key or password file is provided.

#### Requirements:
- `cryptography`
- `hashlib`
- `base64`
- `json`

#### Installation:
1. Clone the repository:

   ```bash
   git clone https://github.com/jasonhejiahuan/python-utilities.git
   cd python-utilities
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

#### Usage:
To run the script, simply execute it:

```bash
python safe-password-V2.0.py
```

The script provides two options:
1. **Encrypt Password**: Enter the password and a hint, and the script will encrypt the password, saving it along with the key in separate files.
2. **Decrypt Password**: Enter the password hint and the key file, and the script will decrypt the stored password and display it.

After encryption, the key is saved in a file (default: `key.key`) and the encrypted password is saved in a file (default: `encrypted-password.enc`). The decryption process requires the same hint and the key file to retrieve the original password.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
