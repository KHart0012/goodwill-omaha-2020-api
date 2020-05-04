#!/usr/bin/env ruby
# frozen_string_literal: true

# Minimally parses a markdown document and generates a markdown formatted
# table of contents, which you can paste back into the document wherever you like
#
# Usage:
#
#     ruby make_toc.rb README.md | pbcopy # or clip or xclip

# Copyright (C) 2020  Alex Gittemeier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def to_anchor(heading)
	heading = heading.downcase.gsub(/[()'’]/, "").tr(" ", "-")
	"#" + heading
end

while (line = gets&.chomp)
	next if line !~ /\A#/

	line_matcher = line.match(/\A(#+) (.+)/)
	if !line_matcher
		warn "#{line} starts with a hash but doesn't look like a header"
		next
	end

	hashes, heading = line_matcher.captures
	indent_level = hashes.length - 1
	next if indent_level == 0

	indent = "   " * (indent_level - 1)
	puts "#{indent}1. [#{heading}](#{to_anchor(heading)})"
end
