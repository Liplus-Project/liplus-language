{
  "openapi": "3.1.1",
  "info": {
    "title": "Li+ GitHub Unified I/O",
    "description": "Issue + PR + CI Polling + Git Data API (Full Compatible / No Base64)",
    "version": "0.1.0"
  },
  "servers": [
    { "url": "https://api.github.com" }
  ],
  "components": {
    "schemas": {},
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    }
  },
  "security": [
    { "BearerAuth": [] }
  ],
  "paths": {

    "/repos/Liplus-Project/liplus-language/issues": {
      "get": {
        "operationId": "listIssues",
        "x-openai-isConsequential": true
      },
      "post": {
        "operationId": "createIssue",
        "x-openai-isConsequential": true,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["title"],
                "properties": {
                  "title": { "type": "string" },
                  "body": { "type": "string" },
                  "labels": {
                    "type": "array",
                    "items": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/issues/{issue_number}": {
      "get": {
        "operationId": "getIssue",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "issue_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      },
      "patch": {
        "operationId": "updateIssue",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "issue_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "title": { "type": "string" },
                  "body": { "type": "string" },
                  "state": { "type": "string", "enum": ["open", "closed"] },
                  "labels": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/issues/{issue_number}/comments": {
      "get": {
        "operationId": "listIssueComments",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "issue_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      },
      "post": {
        "operationId": "createIssueComment",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "issue_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["body"],
                "properties": { "body": { "type": "string" } }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/contents/{path}": {
      "get": {
        "operationId": "getRepoContent",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "path", "in": "path", "required": true, "schema": { "type": "string" } },
          { "name": "ref", "in": "query", "required": false, "schema": { "type": "string" } }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/git/ref/{ref}": {
      "get": {
        "operationId": "getGitRef",
        "x-openai-isConsequential": true,
        "parameters": [
          {
            "name": "ref",
            "in": "path",
            "required": true,
            "schema": { "type": "string" }
          }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/git/blobs": {
      "post": {
        "operationId": "createBlob",
        "x-openai-isConsequential": true,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["content", "encoding"],
                "properties": {
                  "content": { "type": "string" },
                  "encoding": { "type": "string", "enum": ["utf-8"] }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/git/trees": {
      "post": {
        "operationId": "createTree",
        "x-openai-isConsequential": true,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["tree"],
                "properties": {
                  "base_tree": { "type": "string" },
                  "tree": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "required": ["path", "mode", "type", "sha"],
                      "properties": {
                        "path": { "type": "string" },
                        "mode": { "type": "string" },
                        "type": { "type": "string", "enum": ["blob"] },
                        "sha": { "type": "string" }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/git/commits": {
      "post": {
        "operationId": "createCommit",
        "x-openai-isConsequential": true,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["message", "tree", "parents"],
                "properties": {
                  "message": { "type": "string" },
                  "tree": { "type": "string" },
                  "parents": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/git/refs/heads/{branch}": {
      "patch": {
        "operationId": "updateBranchRef",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "branch", "in": "path", "required": true, "schema": { "type": "string" } }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["sha"],
                "properties": {
                  "sha": { "type": "string" },
                  "force": { "type": "boolean", "default": false }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/pulls": {
      "get": {
        "operationId": "listPullRequests",
        "x-openai-isConsequential": true
      },
      "post": {
        "operationId": "createPullRequest",
        "x-openai-isConsequential": true,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["title", "head", "base"],
                "properties": {
                  "title": { "type": "string" },
                  "body": { "type": "string" },
                  "head": { "type": "string" },
                  "base": { "type": "string" },
                  "draft": { "type": "boolean", "default": false }
                }
              }
            }
          }
        }
      }
    },

    "/repos/Liplus-Project/liplus-language/pulls/{pull_number}": {
      "get": {
        "operationId": "getPullRequest",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "pull_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/pulls/{pull_number}/files": {
      "get": {
        "operationId": "listPullRequestFiles",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "pull_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/pulls/{pull_number}/commits": {
      "get": {
        "operationId": "listPullRequestCommits",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "pull_number", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/commits/{ref}/check-runs": {
      "get": {
        "operationId": "listCommitCheckRuns",
        "x-openai-isConsequential": true,
        "parameters": [
          { "name": "ref", "in": "path", "required": true, "schema": { "type": "string" } }
        ]
      }
    },

    "/repos/Liplus-Project/liplus-language/actions/workflows/liplus-ci.yml/runs": {
      "get": {
        "operationId": "listLiplusCiRuns",
        "x-openai-isConsequential": true
      }
    }

  }
}
