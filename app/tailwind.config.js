/** @type {import('tailwindcss').Config} */
module.exports = {
  includeLanguages: {
    jinja: "html",
    jinja2: "html",
  },
  content: ["./**/*.html", "./**/*.jinja"],
  theme: { extend: {} },
  plugins: [],
  hovers: true,
  suggestions: true,
  codeActions: true,
  validate: true,
};
