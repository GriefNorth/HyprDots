return {
	"stevearc/conform.nvim",
	opts = {
		formatters_by_ft = {
			hcl = { "hclfmt" },
			tf = { "hclfmt" },
		},
		formatters = {
			hclfmt = {
				command = "hclfmt",
				stdin = true,
			},
		},
	},
}
