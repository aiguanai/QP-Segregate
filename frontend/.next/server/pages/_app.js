/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "pages/_app";
exports.ids = ["pages/_app"];
exports.modules = {

/***/ "./src/hooks/useAuth.tsx":
/*!*******************************!*\
  !*** ./src/hooks/useAuth.tsx ***!
  \*******************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {\n__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   AuthProvider: () => (/* binding */ AuthProvider),\n/* harmony export */   useAuth: () => (/* binding */ useAuth)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ \"react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! axios */ \"axios\");\n/* harmony import */ var react_hot_toast__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-hot-toast */ \"react-hot-toast\");\nvar __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([axios__WEBPACK_IMPORTED_MODULE_2__, react_hot_toast__WEBPACK_IMPORTED_MODULE_3__]);\n([axios__WEBPACK_IMPORTED_MODULE_2__, react_hot_toast__WEBPACK_IMPORTED_MODULE_3__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);\n\n\n\n\nconst AuthContext = /*#__PURE__*/ (0,react__WEBPACK_IMPORTED_MODULE_1__.createContext)(undefined);\nfunction AuthProvider({ children }) {\n    const [user, setUser] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(null);\n    const [loading, setLoading] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(true);\n    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(()=>{\n        // Check for existing token on mount\n        const token = localStorage.getItem(\"token\");\n        if (token) {\n            // Verify token and get user info\n            verifyToken();\n        } else {\n            setLoading(false);\n        }\n    }, []);\n    const verifyToken = async ()=>{\n        try {\n            const response = await axios__WEBPACK_IMPORTED_MODULE_2__[\"default\"].get(\"/api/auth/me\", {\n                headers: {\n                    Authorization: `Bearer ${localStorage.getItem(\"token\")}`\n                }\n            });\n            setUser(response.data);\n        } catch (error) {\n            localStorage.removeItem(\"token\");\n        } finally{\n            setLoading(false);\n        }\n    };\n    const login = async (username, password, role)=>{\n        setLoading(true);\n        try {\n            // OAuth2PasswordRequestForm expects URL-encoded form data\n            const params = new URLSearchParams();\n            params.append(\"username\", username);\n            params.append(\"password\", password);\n            const response = await axios__WEBPACK_IMPORTED_MODULE_2__[\"default\"].post(\"/api/auth/login\", params.toString(), {\n                headers: {\n                    \"Content-Type\": \"application/x-www-form-urlencoded\"\n                }\n            });\n            const { access_token } = response.data;\n            localStorage.setItem(\"token\", access_token);\n            // Get user info\n            const userResponse = await axios__WEBPACK_IMPORTED_MODULE_2__[\"default\"].get(\"/api/auth/me\", {\n                headers: {\n                    Authorization: `Bearer ${access_token}`\n                }\n            });\n            setUser(userResponse.data);\n            react_hot_toast__WEBPACK_IMPORTED_MODULE_3__[\"default\"].success(\"Login successful!\");\n        } catch (error) {\n            const message = error.response?.data?.detail || \"Login failed\";\n            throw new Error(message);\n        } finally{\n            setLoading(false);\n        }\n    };\n    const logout = ()=>{\n        localStorage.removeItem(\"token\");\n        setUser(null);\n        react_hot_toast__WEBPACK_IMPORTED_MODULE_3__[\"default\"].success(\"Logged out successfully\");\n    };\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(AuthContext.Provider, {\n        value: {\n            user,\n            login,\n            logout,\n            loading\n        },\n        children: children\n    }, void 0, false, {\n        fileName: \"C:\\\\Users\\\\Ashish\\\\QPseg\\\\frontend\\\\src\\\\hooks\\\\useAuth.tsx\",\n        lineNumber: 95,\n        columnNumber: 5\n    }, this);\n}\nfunction useAuth() {\n    const context = (0,react__WEBPACK_IMPORTED_MODULE_1__.useContext)(AuthContext);\n    if (context === undefined) {\n        throw new Error(\"useAuth must be used within an AuthProvider\");\n    }\n    return context;\n}\n\n__webpack_async_result__();\n} catch(e) { __webpack_async_result__(e); } });//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvaG9va3MvdXNlQXV0aC50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7Ozs7O0FBQXNFO0FBRTdDO0FBQ1U7QUFrQm5DLE1BQU1NLDRCQUFjSixvREFBYUEsQ0FBOEJLO0FBRXhELFNBQVNDLGFBQWEsRUFBRUMsUUFBUSxFQUFpQztJQUN0RSxNQUFNLENBQUNDLE1BQU1DLFFBQVEsR0FBR1gsK0NBQVFBLENBQWM7SUFDOUMsTUFBTSxDQUFDWSxTQUFTQyxXQUFXLEdBQUdiLCtDQUFRQSxDQUFDO0lBRXZDQyxnREFBU0EsQ0FBQztRQUNSLG9DQUFvQztRQUNwQyxNQUFNYSxRQUFRQyxhQUFhQyxPQUFPLENBQUM7UUFDbkMsSUFBSUYsT0FBTztZQUNULGlDQUFpQztZQUNqQ0c7UUFDRixPQUFPO1lBQ0xKLFdBQVc7UUFDYjtJQUNGLEdBQUcsRUFBRTtJQUVMLE1BQU1JLGNBQWM7UUFDbEIsSUFBSTtZQUNGLE1BQU1DLFdBQVcsTUFBTWQsaURBQVMsQ0FBQyxnQkFBZ0I7Z0JBQy9DZ0IsU0FBUztvQkFDUEMsZUFBZSxDQUFDLE9BQU8sRUFBRU4sYUFBYUMsT0FBTyxDQUFDLFNBQVMsQ0FBQztnQkFDMUQ7WUFDRjtZQUNBTCxRQUFRTyxTQUFTSSxJQUFJO1FBQ3ZCLEVBQUUsT0FBT0MsT0FBTztZQUNkUixhQUFhUyxVQUFVLENBQUM7UUFDMUIsU0FBVTtZQUNSWCxXQUFXO1FBQ2I7SUFDRjtJQUVBLE1BQU1ZLFFBQVEsT0FBT0MsVUFBa0JDLFVBQWtCQztRQUN2RGYsV0FBVztRQUNYLElBQUk7WUFDRiwwREFBMEQ7WUFDMUQsTUFBTWdCLFNBQVMsSUFBSUM7WUFDbkJELE9BQU9FLE1BQU0sQ0FBQyxZQUFZTDtZQUMxQkcsT0FBT0UsTUFBTSxDQUFDLFlBQVlKO1lBRTFCLE1BQU1ULFdBQVcsTUFBTWQsa0RBQVUsQ0FBQyxtQkFBbUJ5QixPQUFPSSxRQUFRLElBQUk7Z0JBQ3RFYixTQUFTO29CQUNQLGdCQUFnQjtnQkFDbEI7WUFDRjtZQUVBLE1BQU0sRUFBRWMsWUFBWSxFQUFFLEdBQUdoQixTQUFTSSxJQUFJO1lBQ3RDUCxhQUFhb0IsT0FBTyxDQUFDLFNBQVNEO1lBRTlCLGdCQUFnQjtZQUNoQixNQUFNRSxlQUFlLE1BQU1oQyxpREFBUyxDQUFDLGdCQUFnQjtnQkFDbkRnQixTQUFTO29CQUNQQyxlQUFlLENBQUMsT0FBTyxFQUFFYSxhQUFhLENBQUM7Z0JBQ3pDO1lBQ0Y7WUFFQXZCLFFBQVF5QixhQUFhZCxJQUFJO1lBQ3pCakIsK0RBQWEsQ0FBQztRQUNoQixFQUFFLE9BQU9rQixPQUFZO1lBQ25CLE1BQU1lLFVBQVVmLE1BQU1MLFFBQVEsRUFBRUksTUFBTWlCLFVBQVU7WUFDaEQsTUFBTSxJQUFJQyxNQUFNRjtRQUNsQixTQUFVO1lBQ1J6QixXQUFXO1FBQ2I7SUFDRjtJQUVBLE1BQU00QixTQUFTO1FBQ2IxQixhQUFhUyxVQUFVLENBQUM7UUFDeEJiLFFBQVE7UUFDUk4sK0RBQWEsQ0FBQztJQUNoQjtJQUVBLHFCQUNFLDhEQUFDQyxZQUFZb0MsUUFBUTtRQUFDQyxPQUFPO1lBQUVqQztZQUFNZTtZQUFPZ0I7WUFBUTdCO1FBQVE7a0JBQ3pESDs7Ozs7O0FBR1A7QUFFTyxTQUFTbUM7SUFDZCxNQUFNQyxVQUFVMUMsaURBQVVBLENBQUNHO0lBQzNCLElBQUl1QyxZQUFZdEMsV0FBVztRQUN6QixNQUFNLElBQUlpQyxNQUFNO0lBQ2xCO0lBQ0EsT0FBT0s7QUFDVCIsInNvdXJjZXMiOlsid2VicGFjazovL3FwYXBlci1haS1mcm9udGVuZC8uL3NyYy9ob29rcy91c2VBdXRoLnRzeD81ZmFmIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHVzZVN0YXRlLCB1c2VFZmZlY3QsIGNyZWF0ZUNvbnRleHQsIHVzZUNvbnRleHQgfSBmcm9tICdyZWFjdCdcclxuaW1wb3J0IHsgdXNlUm91dGVyIH0gZnJvbSAnbmV4dC9yb3V0ZXInXHJcbmltcG9ydCBheGlvcyBmcm9tICdheGlvcydcclxuaW1wb3J0IHRvYXN0IGZyb20gJ3JlYWN0LWhvdC10b2FzdCdcclxuXHJcbmludGVyZmFjZSBVc2VyIHtcclxuICB1c2VyX2lkOiBudW1iZXJcclxuICB1c2VybmFtZTogc3RyaW5nXHJcbiAgZW1haWw6IHN0cmluZ1xyXG4gIHJvbGU6IHN0cmluZ1xyXG4gIGJyYW5jaF9pZD86IG51bWJlclxyXG4gIGFjYWRlbWljX3llYXI/OiBudW1iZXJcclxufVxyXG5cclxuaW50ZXJmYWNlIEF1dGhDb250ZXh0VHlwZSB7XHJcbiAgdXNlcjogVXNlciB8IG51bGxcclxuICBsb2dpbjogKHVzZXJuYW1lOiBzdHJpbmcsIHBhc3N3b3JkOiBzdHJpbmcsIHJvbGU/OiBzdHJpbmcpID0+IFByb21pc2U8dm9pZD5cclxuICBsb2dvdXQ6ICgpID0+IHZvaWRcclxuICBsb2FkaW5nOiBib29sZWFuXHJcbn1cclxuXHJcbmNvbnN0IEF1dGhDb250ZXh0ID0gY3JlYXRlQ29udGV4dDxBdXRoQ29udGV4dFR5cGUgfCB1bmRlZmluZWQ+KHVuZGVmaW5lZClcclxuXHJcbmV4cG9ydCBmdW5jdGlvbiBBdXRoUHJvdmlkZXIoeyBjaGlsZHJlbiB9OiB7IGNoaWxkcmVuOiBSZWFjdC5SZWFjdE5vZGUgfSkge1xyXG4gIGNvbnN0IFt1c2VyLCBzZXRVc2VyXSA9IHVzZVN0YXRlPFVzZXIgfCBudWxsPihudWxsKVxyXG4gIGNvbnN0IFtsb2FkaW5nLCBzZXRMb2FkaW5nXSA9IHVzZVN0YXRlKHRydWUpXHJcblxyXG4gIHVzZUVmZmVjdCgoKSA9PiB7XHJcbiAgICAvLyBDaGVjayBmb3IgZXhpc3RpbmcgdG9rZW4gb24gbW91bnRcclxuICAgIGNvbnN0IHRva2VuID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oJ3Rva2VuJylcclxuICAgIGlmICh0b2tlbikge1xyXG4gICAgICAvLyBWZXJpZnkgdG9rZW4gYW5kIGdldCB1c2VyIGluZm9cclxuICAgICAgdmVyaWZ5VG9rZW4oKVxyXG4gICAgfSBlbHNlIHtcclxuICAgICAgc2V0TG9hZGluZyhmYWxzZSlcclxuICAgIH1cclxuICB9LCBbXSlcclxuXHJcbiAgY29uc3QgdmVyaWZ5VG9rZW4gPSBhc3luYyAoKSA9PiB7XHJcbiAgICB0cnkge1xyXG4gICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IGF4aW9zLmdldCgnL2FwaS9hdXRoL21lJywge1xyXG4gICAgICAgIGhlYWRlcnM6IHtcclxuICAgICAgICAgIEF1dGhvcml6YXRpb246IGBCZWFyZXIgJHtsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgndG9rZW4nKX1gXHJcbiAgICAgICAgfVxyXG4gICAgICB9KVxyXG4gICAgICBzZXRVc2VyKHJlc3BvbnNlLmRhdGEpXHJcbiAgICB9IGNhdGNoIChlcnJvcikge1xyXG4gICAgICBsb2NhbFN0b3JhZ2UucmVtb3ZlSXRlbSgndG9rZW4nKVxyXG4gICAgfSBmaW5hbGx5IHtcclxuICAgICAgc2V0TG9hZGluZyhmYWxzZSlcclxuICAgIH1cclxuICB9XHJcblxyXG4gIGNvbnN0IGxvZ2luID0gYXN5bmMgKHVzZXJuYW1lOiBzdHJpbmcsIHBhc3N3b3JkOiBzdHJpbmcsIHJvbGU/OiBzdHJpbmcpID0+IHtcclxuICAgIHNldExvYWRpbmcodHJ1ZSlcclxuICAgIHRyeSB7XHJcbiAgICAgIC8vIE9BdXRoMlBhc3N3b3JkUmVxdWVzdEZvcm0gZXhwZWN0cyBVUkwtZW5jb2RlZCBmb3JtIGRhdGFcclxuICAgICAgY29uc3QgcGFyYW1zID0gbmV3IFVSTFNlYXJjaFBhcmFtcygpXHJcbiAgICAgIHBhcmFtcy5hcHBlbmQoJ3VzZXJuYW1lJywgdXNlcm5hbWUpXHJcbiAgICAgIHBhcmFtcy5hcHBlbmQoJ3Bhc3N3b3JkJywgcGFzc3dvcmQpXHJcblxyXG4gICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IGF4aW9zLnBvc3QoJy9hcGkvYXV0aC9sb2dpbicsIHBhcmFtcy50b1N0cmluZygpLCB7XHJcbiAgICAgICAgaGVhZGVyczoge1xyXG4gICAgICAgICAgJ0NvbnRlbnQtVHlwZSc6ICdhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQnXHJcbiAgICAgICAgfVxyXG4gICAgICB9KVxyXG5cclxuICAgICAgY29uc3QgeyBhY2Nlc3NfdG9rZW4gfSA9IHJlc3BvbnNlLmRhdGFcclxuICAgICAgbG9jYWxTdG9yYWdlLnNldEl0ZW0oJ3Rva2VuJywgYWNjZXNzX3Rva2VuKVxyXG5cclxuICAgICAgLy8gR2V0IHVzZXIgaW5mb1xyXG4gICAgICBjb25zdCB1c2VyUmVzcG9uc2UgPSBhd2FpdCBheGlvcy5nZXQoJy9hcGkvYXV0aC9tZScsIHtcclxuICAgICAgICBoZWFkZXJzOiB7XHJcbiAgICAgICAgICBBdXRob3JpemF0aW9uOiBgQmVhcmVyICR7YWNjZXNzX3Rva2VufWBcclxuICAgICAgICB9XHJcbiAgICAgIH0pXHJcblxyXG4gICAgICBzZXRVc2VyKHVzZXJSZXNwb25zZS5kYXRhKVxyXG4gICAgICB0b2FzdC5zdWNjZXNzKCdMb2dpbiBzdWNjZXNzZnVsIScpXHJcbiAgICB9IGNhdGNoIChlcnJvcjogYW55KSB7XHJcbiAgICAgIGNvbnN0IG1lc3NhZ2UgPSBlcnJvci5yZXNwb25zZT8uZGF0YT8uZGV0YWlsIHx8ICdMb2dpbiBmYWlsZWQnXHJcbiAgICAgIHRocm93IG5ldyBFcnJvcihtZXNzYWdlKVxyXG4gICAgfSBmaW5hbGx5IHtcclxuICAgICAgc2V0TG9hZGluZyhmYWxzZSlcclxuICAgIH1cclxuICB9XHJcblxyXG4gIGNvbnN0IGxvZ291dCA9ICgpID0+IHtcclxuICAgIGxvY2FsU3RvcmFnZS5yZW1vdmVJdGVtKCd0b2tlbicpXHJcbiAgICBzZXRVc2VyKG51bGwpXHJcbiAgICB0b2FzdC5zdWNjZXNzKCdMb2dnZWQgb3V0IHN1Y2Nlc3NmdWxseScpXHJcbiAgfVxyXG5cclxuICByZXR1cm4gKFxyXG4gICAgPEF1dGhDb250ZXh0LlByb3ZpZGVyIHZhbHVlPXt7IHVzZXIsIGxvZ2luLCBsb2dvdXQsIGxvYWRpbmcgfX0+XHJcbiAgICAgIHtjaGlsZHJlbn1cclxuICAgIDwvQXV0aENvbnRleHQuUHJvdmlkZXI+XHJcbiAgKVxyXG59XHJcblxyXG5leHBvcnQgZnVuY3Rpb24gdXNlQXV0aCgpIHtcclxuICBjb25zdCBjb250ZXh0ID0gdXNlQ29udGV4dChBdXRoQ29udGV4dClcclxuICBpZiAoY29udGV4dCA9PT0gdW5kZWZpbmVkKSB7XHJcbiAgICB0aHJvdyBuZXcgRXJyb3IoJ3VzZUF1dGggbXVzdCBiZSB1c2VkIHdpdGhpbiBhbiBBdXRoUHJvdmlkZXInKVxyXG4gIH1cclxuICByZXR1cm4gY29udGV4dFxyXG59XHJcbiJdLCJuYW1lcyI6WyJ1c2VTdGF0ZSIsInVzZUVmZmVjdCIsImNyZWF0ZUNvbnRleHQiLCJ1c2VDb250ZXh0IiwiYXhpb3MiLCJ0b2FzdCIsIkF1dGhDb250ZXh0IiwidW5kZWZpbmVkIiwiQXV0aFByb3ZpZGVyIiwiY2hpbGRyZW4iLCJ1c2VyIiwic2V0VXNlciIsImxvYWRpbmciLCJzZXRMb2FkaW5nIiwidG9rZW4iLCJsb2NhbFN0b3JhZ2UiLCJnZXRJdGVtIiwidmVyaWZ5VG9rZW4iLCJyZXNwb25zZSIsImdldCIsImhlYWRlcnMiLCJBdXRob3JpemF0aW9uIiwiZGF0YSIsImVycm9yIiwicmVtb3ZlSXRlbSIsImxvZ2luIiwidXNlcm5hbWUiLCJwYXNzd29yZCIsInJvbGUiLCJwYXJhbXMiLCJVUkxTZWFyY2hQYXJhbXMiLCJhcHBlbmQiLCJwb3N0IiwidG9TdHJpbmciLCJhY2Nlc3NfdG9rZW4iLCJzZXRJdGVtIiwidXNlclJlc3BvbnNlIiwic3VjY2VzcyIsIm1lc3NhZ2UiLCJkZXRhaWwiLCJFcnJvciIsImxvZ291dCIsIlByb3ZpZGVyIiwidmFsdWUiLCJ1c2VBdXRoIiwiY29udGV4dCJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/hooks/useAuth.tsx\n");

/***/ }),

/***/ "./src/pages/_app.tsx":
/*!****************************!*\
  !*** ./src/pages/_app.tsx ***!
  \****************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {\n__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var react_query__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-query */ \"react-query\");\n/* harmony import */ var react_query__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_query__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var react_hot_toast__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-hot-toast */ \"react-hot-toast\");\n/* harmony import */ var _hooks_useAuth__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../hooks/useAuth */ \"./src/hooks/useAuth.tsx\");\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../styles/globals.css */ \"./src/styles/globals.css\");\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_styles_globals_css__WEBPACK_IMPORTED_MODULE_4__);\nvar __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([react_hot_toast__WEBPACK_IMPORTED_MODULE_2__, _hooks_useAuth__WEBPACK_IMPORTED_MODULE_3__]);\n([react_hot_toast__WEBPACK_IMPORTED_MODULE_2__, _hooks_useAuth__WEBPACK_IMPORTED_MODULE_3__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);\n\n\n\n\n\nconst queryClient = new react_query__WEBPACK_IMPORTED_MODULE_1__.QueryClient();\nfunction App({ Component, pageProps }) {\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(react_query__WEBPACK_IMPORTED_MODULE_1__.QueryClientProvider, {\n        client: queryClient,\n        children: /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(_hooks_useAuth__WEBPACK_IMPORTED_MODULE_3__.AuthProvider, {\n            children: [\n                /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Component, {\n                    ...pageProps\n                }, void 0, false, {\n                    fileName: \"C:\\\\Users\\\\Ashish\\\\QPseg\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n                    lineNumber: 13,\n                    columnNumber: 9\n                }, this),\n                /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(react_hot_toast__WEBPACK_IMPORTED_MODULE_2__.Toaster, {\n                    position: \"top-right\"\n                }, void 0, false, {\n                    fileName: \"C:\\\\Users\\\\Ashish\\\\QPseg\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n                    lineNumber: 14,\n                    columnNumber: 9\n                }, this)\n            ]\n        }, void 0, true, {\n            fileName: \"C:\\\\Users\\\\Ashish\\\\QPseg\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n            lineNumber: 12,\n            columnNumber: 7\n        }, this)\n    }, void 0, false, {\n        fileName: \"C:\\\\Users\\\\Ashish\\\\QPseg\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n        lineNumber: 11,\n        columnNumber: 5\n    }, this);\n}\n\n__webpack_async_result__();\n} catch(e) { __webpack_async_result__(e); } });//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvcGFnZXMvX2FwcC50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7Ozs7OztBQUM4RDtBQUNyQjtBQUNNO0FBQ2pCO0FBRTlCLE1BQU1JLGNBQWMsSUFBSUosb0RBQVdBO0FBRXBCLFNBQVNLLElBQUksRUFBRUMsU0FBUyxFQUFFQyxTQUFTLEVBQVk7SUFDNUQscUJBQ0UsOERBQUNOLDREQUFtQkE7UUFBQ08sUUFBUUo7a0JBQzNCLDRFQUFDRCx3REFBWUE7OzhCQUNYLDhEQUFDRztvQkFBVyxHQUFHQyxTQUFTOzs7Ozs7OEJBQ3hCLDhEQUFDTCxvREFBT0E7b0JBQUNPLFVBQVM7Ozs7Ozs7Ozs7Ozs7Ozs7O0FBSTFCIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vcXBhcGVyLWFpLWZyb250ZW5kLy4vc3JjL3BhZ2VzL19hcHAudHN4P2Y5ZDYiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHR5cGUgeyBBcHBQcm9wcyB9IGZyb20gJ25leHQvYXBwJ1xyXG5pbXBvcnQgeyBRdWVyeUNsaWVudCwgUXVlcnlDbGllbnRQcm92aWRlciB9IGZyb20gJ3JlYWN0LXF1ZXJ5J1xyXG5pbXBvcnQgeyBUb2FzdGVyIH0gZnJvbSAncmVhY3QtaG90LXRvYXN0J1xyXG5pbXBvcnQgeyBBdXRoUHJvdmlkZXIgfSBmcm9tICcuLi9ob29rcy91c2VBdXRoJ1xyXG5pbXBvcnQgJy4uL3N0eWxlcy9nbG9iYWxzLmNzcydcclxuXHJcbmNvbnN0IHF1ZXJ5Q2xpZW50ID0gbmV3IFF1ZXJ5Q2xpZW50KClcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIEFwcCh7IENvbXBvbmVudCwgcGFnZVByb3BzIH06IEFwcFByb3BzKSB7XHJcbiAgcmV0dXJuIChcclxuICAgIDxRdWVyeUNsaWVudFByb3ZpZGVyIGNsaWVudD17cXVlcnlDbGllbnR9PlxyXG4gICAgICA8QXV0aFByb3ZpZGVyPlxyXG4gICAgICAgIDxDb21wb25lbnQgey4uLnBhZ2VQcm9wc30gLz5cclxuICAgICAgICA8VG9hc3RlciBwb3NpdGlvbj1cInRvcC1yaWdodFwiIC8+XHJcbiAgICAgIDwvQXV0aFByb3ZpZGVyPlxyXG4gICAgPC9RdWVyeUNsaWVudFByb3ZpZGVyPlxyXG4gIClcclxufVxyXG4iXSwibmFtZXMiOlsiUXVlcnlDbGllbnQiLCJRdWVyeUNsaWVudFByb3ZpZGVyIiwiVG9hc3RlciIsIkF1dGhQcm92aWRlciIsInF1ZXJ5Q2xpZW50IiwiQXBwIiwiQ29tcG9uZW50IiwicGFnZVByb3BzIiwiY2xpZW50IiwicG9zaXRpb24iXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/pages/_app.tsx\n");

/***/ }),

/***/ "./src/styles/globals.css":
/*!********************************!*\
  !*** ./src/styles/globals.css ***!
  \********************************/
/***/ (() => {



/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "react" ***!
  \************************/
/***/ ((module) => {

"use strict";
module.exports = require("react");

/***/ }),

/***/ "react-query":
/*!******************************!*\
  !*** external "react-query" ***!
  \******************************/
/***/ ((module) => {

"use strict";
module.exports = require("react-query");

/***/ }),

/***/ "react/jsx-dev-runtime":
/*!****************************************!*\
  !*** external "react/jsx-dev-runtime" ***!
  \****************************************/
/***/ ((module) => {

"use strict";
module.exports = require("react/jsx-dev-runtime");

/***/ }),

/***/ "axios":
/*!************************!*\
  !*** external "axios" ***!
  \************************/
/***/ ((module) => {

"use strict";
module.exports = import("axios");;

/***/ }),

/***/ "react-hot-toast":
/*!**********************************!*\
  !*** external "react-hot-toast" ***!
  \**********************************/
/***/ ((module) => {

"use strict";
module.exports = import("react-hot-toast");;

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = (__webpack_exec__("./src/pages/_app.tsx"));
module.exports = __webpack_exports__;

})();