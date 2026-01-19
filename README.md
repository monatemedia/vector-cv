<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/monatemedia/vector-cv">
    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135679.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Vector CV: Resume Synthesizer</h3>

  <p align="center">
    An AI-powered RAG system that stores your career history as vector embeddings and synthesizes tailored CVs based on specific job descriptions.
    <br />
    <a href="https://github.com/monatemedia/vector-cv"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/monatemedia/vector-cv">View Demo</a>
    &middot;
    <a href="https://github.com/monatemedia/vector-cv/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/monatemedia/vector-cv/issues">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

Vector CV solves the "one-size-fits-all" resume problem. Using a Retrieval-Augmented Generation (RAG) stack, it selects only the most semantically relevant experience blocks for a specific job application, ensuring your CV is always perfectly tailored.

**Key Features:**
* **Master Profile Storage** - Semantic storage of work history using `pgvector`.
* **Hybrid Selection Strategy** - Combines pillar projects, specific skill matching, and vector similarity search.
* **Skills Gap Analysis** - Identifies missing requirements before you apply.
* **Automated Document Export** - Generates `.docx` files for CVs and Cover Letters.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![React][React-badge]][React-url]
* [![PostgreSQL][Postgres-badge]][Postgres-url]
* [![OpenAI][OpenAI-badge]][OpenAI-url]
* [![Docker][Docker-badge]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

* **Docker & Docker Compose**
* **Python 3.10+** and **Pipenv**
* **Node.js & npm**

### Installation

1. Clone the repo
   ```sh
   git clone [https://github.com/monatemedia/vector-cv.git](https://github.com/monatemedia/vector-cv.git)

```

2. Create your `.env` file from the template
```sh
cp .env.example .env
# Add your OPENAI_API_KEY and Database credentials

```


3. Install dependencies (Root, Backend, and Frontend)
```sh
make install

```


4. Start the environment and open the browser
```sh
make all

```



<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### 1. Initialize the Database

If running for the first time, seed your master profile:

```sh
make seed

```

### 2. Tailor a CV

1. Access the dashboard at `http://localhost:5173`.
2. Paste the Job Description.
3. Review the **Skills Gap Analysis**.
4. Download your generated `.docx` CV and Cover Letter.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

* [x] Vector Similarity Search (pgvector)
* [x] Skills Gap Analysis
* [x] Word Document (.docx) Generation
* [ ] PDF Export functionality
* [ ] Multi-user Authentication
* [ ] Direct Email integration for applications

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Your Name - [@monatemedia](https://www.google.com/search?q=https://twitter.com/monatemedia) - email@example.com

Project Link: [https://github.com/monatemedia/vector-cv](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/monatemedia/vector-cv)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
