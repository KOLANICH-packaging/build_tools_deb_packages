#!/usr/bin/env python3
"""Builds packages"""
import sys
from pathlib import Path
from prebuilder.systems import CMake, Make
from prebuilder.distros.debian import Debian
from prebuilder.buildPipeline import BuildPipeline, BuildRecipy
from prebuilder.repoPipeline import RepoPipelineMeta
from prebuilder.core.Package import PackageMetadata
from prebuilder.core.Package import PackageRef, VersionedPackageRef
from prebuilder.fetchers.GitRepoFetcher import GitRepoFetcher
from fsutilz import movetree, copytree
from ClassDictMeta import ClassDictMeta

thisDir = Path(".").absolute()




premakeMeta = {
	"descriptionShort": "cross-platform build script generator",
	"descriptionLong": "premake allows you to manage your project configuration in one place and still support those pesky IDE-addicted Windows coders and/or cranky Linux command-line junkies. It allows you to generate project files for tools that you do not own. It saves the time that would otherwise be spent manually keeping several different toolsets in sync. And it provides an easy upgrade path as new versions of your favorite tools are released.",
	"license": "BSD-3-Clause",
	"section": "devel",
}
def premakeInstallRule(sourceDir, buildDir, pkg, gnuDirs):
	copytree((sourceDir / "bin" / "release" / "premake5"), pkg.nest(gnuDirs.prefix) / "bin"/ "premake5")



class build(metaclass=RepoPipelineMeta):
	"""It's {maintainerName}'s repo for {repoKind} packages of build tools."""
	
	DISTROS = (Debian,)
	
	def bake():
		repoURI = "https://github.com/SanderMertens/bake"
		
		def installRule(sourceDir, buildDir, pkg, gnuDirs):
			copytree((sourceDir / ".." / "bake"), pkg.nest(gnuDirs.prefix)/"bin"/ "bake")
			copytree((sourceDir / ".." / "include"), pkg.nest(gnuDirs.prefix)/"include")
		
		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "A build system that lets you clone, build and run C/C++ projects with a single command"
			descriptionLong = """
To that end, bake is a build tool, build system, package manager and environment manager in one. Bake automates building code, especially for highly interdependent projects. Currently, Bake's focus is C/C++.

Bake's main features are:
	discover all projects in current directory & build them in the correct order
	clone, build and run a project and its dependencies with a single command using bake bundles
	automatically include header files from dependencies
	use logical (hierarchical) identifiers to specify dependencies on any project built on the machine
	programmable C API for interacting with package management
	manage and automatically export environment variables used for builds

Bake depends on git for its package management features, and does not have a server infrastructure for hosting a package repository. Bake does not collect any information when you clone, build or publish projects."""
			license = "MIT"
			depends = ()
			section = "devel"
			homepage = repoURI
		
		bakeBuildRecipy = BuildRecipy(Make, GitRepoFetcher(repoURI, refspec="master"), buildOptions = {}, useKati=True, configureScript=None, installRule=installRule, subdir="build-Linux")
		bakeMetadata = PackageMetadata("bake", **cfg)
		
		return BuildPipeline(bakeBuildRecipy, ((Debian, bakeMetadata),))

	def CLI11():
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher("https://github.com/CLIUtils/CLI11", "master"), buildOptions = {"CLI11_BUILD_DOCS":False, "CLI11_BUILD_EXAMPLES":False, "CLI11_INSTALL":True, "BUILD_TESTING":False, }, patches = [(thisDir / "patches" / "CLI11")])
		metadata = PackageMetadata(PackageRef("cli11"))
		
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def kati():
		repoURI = "https://github.com/google/kati"
		#repoURI = "https://github.com/KOLANICH/kati" # ref CLI11
		cfg = {
			"descriptionShort": "An experimental GNU make clone",
			"descriptionLong": "kati is an experimental GNU make clone. The main goal of this tool is to speed-up incremental build of Android. Currently, kati does not offer a faster build by itself. It instead converts your Makefile to a ninja file.",
			# "license": "MIT",
			"depends": (),
			"recommends": ("ninja-build",),
			"section": "devel",
			"homepage": repoURI,
		}
		
		def installRule(sourceDir, buildDir, pkg, gnuDirs):
			copytree((sourceDir / "ckati"), pkg.nest(gnuDirs.prefix) / "bin"/ "ckati")
		
		katiBuildRecipy = BuildRecipy(Make, GitRepoFetcher(repoURI, "master"), buildOptions = {}, useKati=True, configureScript=None, installRule=installRule,
			patches = [(thisDir / "patches" / "kati")]
		)
		katiMetadata = PackageMetadata(VersionedPackageRef("kati", version="0.0-git"), **cfg)
		
		return BuildPipeline(katiBuildRecipy, ((Debian, katiMetadata),))
	
	def premake_bootstrap():
		repoURI = "https://github.com/premake/premake-core"
		cfg = {
			"homepage": repoURI,
			**premakeMeta
		}
		
		
		buildRecipy = BuildRecipy(Make, GitRepoFetcher(repoURI, "master"), buildOptions = {}, useKati=False, configureScript=None, installRule=premakeInstallRule, makeArgs=("-f", "Bootstrap.mak", "linux"), firejailCfg={"apparmor":False})
		metadata = PackageMetadata(PackageRef("premake", versionPostfix=1), **cfg)
		return BuildPipeline(buildRecipy, ((Debian, metadata),))
	
	def _premake():
		repoURI = "https://github.com/premake/premake-core"
		cfg = {
			"homepage": repoURI,
			**premakeMeta
		}
		
		def installRule(sourceDir, buildDir, pkg, gnuDirs):
			copytree((sourceDir / "bin" / "release" / "premake5"), pkg.nest(gnuDirs.prefix) / "bin"/ "premake5")
		
		buildRecipy = BuildRecipy(Premake5, GitRepoFetcher(repoURI, "master"), buildOptions = {}, useKati=True, configureScript=None, installRule=premakeInstallRule, firejailCfg={"apparmor": False})
		metadata = PackageMetadata(PackageRef("premake", versionPostfix=1), **cfg)
		return BuildPipeline(buildRecipy, ((Debian, metadata),))
	
	def ninja():
		repoURI = "https://github.com/ninja-build/ninja"
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher(repoURI, "master"), buildOptions = {"CMAKE_UNITY_BUILD": False}
		, patches = [(thisDir / "patches" / "ninja")]
		)
		metadata = PackageMetadata(PackageRef("ninja-build"))
		
		return BuildPipeline(buildRecipy, ((Debian, metadata),))


if __name__ == "__main__":
	build()
