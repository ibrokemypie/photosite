const requireArrowFunctionsPlugin = {
  name: "require-arrow-functions",
  rules: {
    "require-arrow-functions": {
      create(context) {
        return {
          FunctionDeclaration(node) {
            context.report({
              node,
              message: "Use arrow funcs, not functions.",
            });
          },
          FunctionExpression(node) {
            if (node.type !== "ArrowFunctionExpression") {
              context.report({
                node,
                message: "Use arrow funcs, not functions.",
              });
            }
          },
        };
      },
    },
  },
};

export default requireArrowFunctionsPlugin;
