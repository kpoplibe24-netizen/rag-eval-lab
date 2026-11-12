# Failure worksheet (14 questions)

## 1. Can I define more than one response for a FastAPI path operation?
- Expected: `advanced/path-operation-advanced-configuration.md | Additional Responses` (rank: 7)
- Got #1: `tutorial/response-model.md | `response_model` Priority`
- Got #2: `tutorial/path-operation-configuration.md | Response description`
- Got #3: `advanced/generate-clients.md | Custom Generate Unique ID Function`
- Expected section starts: You probably have seen how to declare the `response_model` and `status_code` for a *path operation*.  That defines the metadata about the main response of a *path operation*.  You can also declare additional responses with their models, status codes, etc.  There's a whole chapter here in the documentation about it, you can read it at [Additional Responses in OpenAPI](additional-responses.md).
- **Category:** Near miss (right page , wrong section)

## 2. How does FastAPI recognize and handle a path operation that returns a `Response` object directly?
- Expected: `tutorial/response-model.md | Return a Response Directly` (rank: None)
- Got #1: `advanced/response-directly.md | How a Response Model Works`
- Got #2: `advanced/response-directly.md | Return a Response Directly`
- Got #3: `advanced/response-headers.md | Use a `Response` parameter`
- Expected section starts: The most common case would be [returning a Response directly as explained later in the advanced docs](../advanced/response-directly.md).    This simple case is handled automatically by FastAPI because the return type annotation is the class (or a subclass of) `Response`.  And tools will also be happy because both `RedirectResponse` and `JSONResponse` are subclasses of `Response`, so the type annotation is correct.
- **Category:** Near miss (right page , wrong section)

## 3. How can I define a custom response type in FastAPI?
- Expected: `advanced/custom-response.md | Custom response class` (rank: None)
- Got #1: `advanced/custom-response.md | Custom Response - HTML, Stream, File, others`
- Got #2: `advanced/additional-responses.md | Additional media types for the main response`
- Got #3: `tutorial/response-model.md | Annotate a Response Subclass`
- Expected section starts: You can create your own custom response class, inheriting from `Response` and using it.  For example, let's say that you want to use [`orjson`](https://github.com/ijl/orjson) with some settings.  Let's say you want it to return indented and formatted JSON, so you want to use the orjson option `orjson.OPT_INDENT_2`.  You could create a `CustomORJSONResponse`. The main thing you have to do is create a `Response.render(content)` method that returns the content as `bytes`:    Now instead of returnin
- **Category:** Near miss (right page , wrong section)

## 4. How do I start a minimal FastAPI application and identify the local URL where the server is running?
- Expected: `tutorial/first-steps.md | First Steps` (rank: None)
- Got #1: `advanced/behind-a-proxy.md | Additional servers`
- Got #2: `advanced/sub-applications.md | Technical Details: `root_path``
- Got #3: `advanced/behind-a-proxy.md | Enable Proxy Forwarded Headers`
- Expected section starts: The simplest FastAPI file could look like this:    Copy that to a file `main.py`.  /// tip  FastAPI has an [official extension for VS Code](https://marketplace.visualstudio.com/items?itemName=FastAPILabs.fastapi-vscode) (and Cursor), which provides a lot of features, including a path operation explorer, path operation search, CodeLens navigation in tests (jump to definition from tests), and FastAPI Cloud deployment and logs, all from your editor.  ///  Run the live server:        In the output, 
- **Category:** Term Collision 

## 5. What does FastAPI do with a dependency that uses yield internally?
- Expected: `tutorial/dependencies/dependencies-with-yield.md | What are "Context Managers"` (rank: 7)
- Got #1: `tutorial/dependencies/dependencies-with-yield.md | Dependencies with yield`
- Got #2: `tutorial/dependencies/dependencies-with-yield.md | Sub-dependencies with `yield``
- Got #3: `advanced/advanced-dependencies.md | Dependencies with `yield` and `except`, Technical Details`
- Expected section starts: "Context Managers" are any of those Python objects that you can use in a `with` statement.  For example, [you can use `with` to read a file](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files):    Underneath, the `open("./somefile.txt")` creates an object that is called a "Context Manager".  When the `with` block finishes, it makes sure to close the file, even if there were exceptions.  When you create a dependency with `yield`, **FastAPI** will internally create a con
- **Category:** Near miss (right page , wrong section)

## 6. How can I send a sequence of JSON objects from a FastAPI endpoint without returning the entire list at once?
- Expected: `tutorial/stream-json-lines.md | Stream JSON Lines with FastAPI` (rank: 7)
- Got #1: `tutorial/stream-json-lines.md | Stream JSON Lines`
- Got #2: `advanced/response-directly.md | Return a Response Directly`
- Got #3: `tutorial/stream-json-lines.md | JSON Lines`
- Expected section starts: To stream JSON Lines with FastAPI you can, instead of using `return` in your *path operation function*, use `yield` to produce each item in turn.    If each JSON item you want to send back is of type `Item` (a Pydantic model) and it's an async function, you can declare the return type as `AsyncIterable[Item]`:    If you declare the return type, FastAPI will use it to **validate** the data, **document** it in OpenAPI, **filter** it, and **serialize** it using Pydantic.  /// tip  As Pydantic will 
- **Category:** Near miss (right page , wrong section)

## 7. What is the simplest way to serve a directory of static assets in FastAPI?
- Expected: `tutorial/static-files.md | Use `StaticFiles`` (rank: 7)
- Got #1: `tutorial/static-files.md | Details`
- Got #2: `tutorial/frontend.md | Frontend`
- Got #3: `tutorial/frontend.md | Serve a Frontend`
- Expected section starts: * Import `StaticFiles`. * "Mount" a `StaticFiles()` instance in a specific path.    /// note | Technical Details  You could also use `from starlette.staticfiles import StaticFiles`.  **FastAPI** provides the same `starlette.staticfiles` as `fastapi.staticfiles` just as a convenience for you, the developer. But it actually comes directly from Starlette.  ///
- **Category:** Near miss (right page , wrong section)

## 8. What types of data and special formats does FastAPI support for validation through Pydantic?
- Expected: `features.md | Validation` (rank: 8)
- Got #1: `tutorial/path-params.md | Pydantic`
- Got #2: `advanced/dataclasses.md | Using Dataclasses`
- Got #3: `tutorial/response-model.md | FastAPI Data Filtering`
- Expected section starts: * Validation for most (or all?) Python **data types**, including:     * JSON objects (`dict`).     * JSON array (`list`) defining item types.     * String (`str`) fields, defining min and max lengths.     * Numbers (`int`, `float`) with min and max values, etc.  * Validation for more exotic types, like:     * URL.     * Email.     * UUID.     * ...and others.  All the validation is handled by the well-established and robust **Pydantic**.
- **Category:** Vocabulary mismatch

## 9. How can I move my FastAPI configuration into a separate Python module?
- Expected: `advanced/settings.md | Settings in another module` (rank: None)
- Got #1: `tutorial/index.md | Tutorial - User Guide`
- Got #2: `tutorial/bigger-applications.md | The main `FastAPI``
- Got #3: `advanced/advanced-python-types.md | Using `Union` or `Optional``
- Expected section starts: You could put those settings in another module file as you saw in [Bigger Applications - Multiple Files](../tutorial/bigger-applications.md).  For example, you could have a file `config.py` with:    And then use it in a file `main.py`:    /// tip  You would also need a file `__init__.py` as you saw in [Bigger Applications - Multiple Files](../tutorial/bigger-applications.md).  ///
- **Category:** Weak question

## 10. What is a way to share security and dependency logic across many FastAPI routes without repeating code?
- Expected: `tutorial/security/get-current-user.md | Code size` (rank: None)
- Got #1: `tutorial/dependencies/index.md | What is "Dependency Injection"`
- Got #2: `tutorial/bigger-applications.md | Include an `APIRouter` in another`
- Got #3: `tutorial/security/first-steps.md | Use it`
- Expected section starts: This example might seem verbose. Keep in mind that we are mixing security, data models, utility functions and *path operations* in the same file.  But here's the key point.  The security and dependency injection stuff is written once.  And you can make it as complex as you want. And still, have it written only once, in a single place. With all the flexibility.  But you can have thousands of endpoints (*path operations*) using the same security system.  And all of them (or any portion of them tha
- **Category:** Near miss (right page , wrong section)

## 11. How can I exclude the password field from being sent back in an API response?
- Expected: `tutorial/response-model.md | Add an output model` (rank: 7)
- Got #1: `tutorial/security/first-steps.md | The `password` flow`
- Got #2: `tutorial/security/oauth2-jwt.md | Password hashing`
- Got #3: `tutorial/security/simple-oauth2.md | Use the form data`
- Expected section starts: We can instead create an input model with the plaintext password and an output model without it:    Here, even though our *path operation function* is returning the same input user that contains the password:    ...we declared the `response_model` to be our model `UserOut`, that doesn't include the password:    So, **FastAPI** will take care of filtering out all the data that is not declared in the output model (using Pydantic).
- **Category:** Term collision

## 12. How can I enforce specific OAuth scopes on a FastAPI endpoint using Security?
- Expected: `advanced/security/oauth2-scopes.md | Declare scopes in *path operations* and dependencies` (rank: None)
- Got #1: `advanced/security/oauth2-scopes.md | OAuth2 scopes`
- Got #2: `tutorial/security/oauth2-jwt.md | Advanced usage with `scopes``
- Got #3: `advanced/security/oauth2-scopes.md | OAuth2 scopes and OpenAPI`
- Expected section starts: Now we declare that the *path operation* for `/users/me/items/` requires the scope `items`.  For this, we import and use `Security` from `fastapi`.  You can use `Security` to declare dependencies (just like `Depends`), but `Security` also receives a parameter `scopes` with a list of scopes (strings).  In this case, we pass a dependency function `get_current_active_user` to `Security` (the same way we would do with `Depends`).  But we also pass a `list` of scopes, in this case with just one scope
- **Category:** Near miss (right page , wrong section)

## 13. How can I retrieve the security scopes inside a dependency without using the Security wrapper?
- Expected: `advanced/security/oauth2-scopes.md | Use `SecurityScopes`` (rank: 6)
- Got #1: `advanced/security/oauth2-scopes.md | More details about `SecurityScopes``
- Got #2: `advanced/security/oauth2-scopes.md | Declare scopes in *path operations* and dependencies`
- Got #3: `advanced/security/oauth2-scopes.md | Verify the `scopes``
- Expected section starts: Now update the dependency `get_current_user`.  This is the one used by the dependencies above.  Here's where we are using the same OAuth2 scheme we created before, declaring it as a dependency: `oauth2_scheme`.  Because this dependency function doesn't have any scope requirements itself, we can use `Depends` with `oauth2_scheme`, we don't have to use `Security` when we don't need to specify security scopes.  We also declare a special parameter of type `SecurityScopes`, imported from `fastapi.sec
- **Category:** Near miss (right page , wrong section)

## 14. How can I indicate that a query parameter is deprecated so it shows up that way in the documentation?
- Expected: `tutorial/query-params-str-validations.md | Deprecating parameters` (rank: 6)
- Got #1: `tutorial/query-params-str-validations.md | Add `Query` to `Annotated` in the `q` parameter`
- Got #2: `tutorial/query-params.md | Optional parameters`
- Got #3: `tutorial/query-params-str-validations.md | Alternative (old): `Query` as the default value`
- Expected section starts: Now let's say you don't like this parameter anymore.  You have to leave it there a while because there are clients using it, but you want the docs to clearly show it as deprecated.  Then pass the parameter `deprecated=True` to `Query`:    The docs will show it like this:
- **Category:** Near miss (right page , wrong section)
