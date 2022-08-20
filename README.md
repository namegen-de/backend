# Database & Backend

:namegen uses a Flask (Python) backend to 

1. serve the machine learning model (RNN) to generate names based on user-specific query parameters 
2. handle user-related data (user authentification) so that registered users can store and save names they like

The entire backend structure is hosted on [Heroku](https://www.heroku.com/). Two separate heroku applications are running on
:europe: european servers ([Mode]: Hobby Dev (free)):

1. `namegen-backend-staging` - for testing new features in the same environment
2. `namegen-backend-production` - the released production environment (frontend queries from the official [namegen](https://wwww.namegen.de)) website go there)

Both apps are locally stored in the `backend` repository and the two remotes are called `heroku-staging` and `heroku-production`.

## Heroku Addons

The backend uses a simple PostgreSQL database (for storing user-related data) and a RedisServer (for server-side sessions for secure user authentification).
Both addons are free for use (with limited storage capacities and features) and are added to the staging and production apps.

## Workflow (deploying to `sta` or `pro`)

New features are built locally in the `dev` branch of the repository. 
If preferred, for each new features a feature branch `feature/<feature-name>` could be created and merged into `dev` once finished.
This workflow is not really necessary in the absence of many collaborators - so I will probably stick to developing on the `dev` branch and have a one-commit-one-feature policy.
To run the backend server on port `5000`, type 

```
heroku local -p 5000
```

*Environment variables are loaded from a `.env` file in the root directory (which is git ignored). To run the same environemnt as staging run write the staging environment into a `.env` with `heroku config -s > .env`*


Once a set of features is developed and ready to be published to production as a new app version, the `dev` branch is merged into `staging` via

```bash
git checkout staging && git merge dev
```

This will merge all new features into staging. Save the changes first to the git remote (which is linked ot pushing by default) via 

```bash
git push [origin staging]
```

and finally to heroku (here we have to use a little trick to push from a local git branch to a remote branch with another name)

```bash
git push heroku-staging staging:main
```

This should upload the changes to heroku and the built of the app should start. Check out the backend changes at [https://namegen-backend-staging.herokuapp.com/](https://namegen-backend-staging.herokuapp.com/)

If the backend works as expected, then follow the same logic with the production branch. First merge `staging` into `main` and then publish to the git and heroku remote

```bash
git checkout main && git merge staging
git push
git push heroku-production main
```

Check out the new production version at [https://namegen-backend-staging.herokuapp.com/](https://namegen-backend-staging.herokuapp.com/)

## Using Heroku CLI

The Heroku CLI offers neat functionality for debugging and testing the application.

- `heroku log -r [remote]` to see the logs of the currently deployed app
- `heroku env -r [remote]` to see the environment variables saved in the heroku environment
- `heroku env:set [key]=[val] -r [remote]` to set an environment variables saved in the heroku environment
- `heroku env:unset [key]=[val] -r [remote]` to set an environment variables saved in the heroku environment
- `heroku run bash -r [remote]` to open a remote bash session on the heroku server
