package org.applause.util.xcode.project

import com.google.inject.Inject
import org.applause.util.xcode.projectfile.pbxproj.ProductType
import org.jnario.runner.CreateWith

import static extension org.applause.util.xcode.project.Path.*
import static extension org.jnario.lib.Should.*

/**
 * `XcodeProject`s are a high-level API to create and read `.pbxproj` files. Internally, it uses the 
 * Pbxproject metamodel as defined by `pbxproj.xtext` and provides an easy-to-use high-level API for it. 
 */
@CreateWith(typeof(PbxprojSpecCreator))
describe XcodeProject {
	@Inject XcodeProjectFactory projectFactory
	
	context 'Creating projects' {
		fact 'A project can be created without a path' {
			new XcodeProject() // but does this make sense?
		}
		
		/**
		 * TODO can we create projects wihout using the project factory?
		 */
		fact 'A project can be created with a path' {
			val project = projectFactory.create('/foo/bar')
			project.pbxProjectFileName should be '/foo/bar/project.pbxproj'
		}
	}
	
	context 'Project properties' {
		/**
		 * A project has a number of attributes that are used by Xcode and other IDEs, mainly to
		 * derive information such as the copyright string.
		 */
		context 'Project attributes' {
			/**
			 * TODO: Do Xcode and other tools use the organization name to create the copyright string? 
			 */
			fact 'Organization name' {
				val project = projectFactory.create('/foo/bar')
				project.organizationName = 'Peter Friese'
				project.organizationName should be 'Peter Friese'
			}
			
			/**
			 * The class prefix is used by Xcode wizards to suggest class names.
			 */
			fact 'Class prefix' {
				val project = projectFactory.create('/foo/bar')
				project.classPrefix = 'FOO'
				project.classPrefix should be 'FOO'
			}
			
			/**
			 * LastUpgradeCheck seems to reflect the version number of Xcode.
			 * TODO Check this.
			 */
			fact 'Last update check' {
				val project = projectFactory.create('/foo/bar')
				assert project.lastUpgradeCheck >= 440				
			}
		}
		
		/**
		 * There are more IDE-related properties which are not stored in the `attributes` section of 
		 * a project, but rather in the main project node.
		 */
		context 'More IDE-related properties' {
			
			/** 
			 * Xcode project files can either be Xcode 3.1 or Xcode 3.2 compatible.
			 * Usually, modern Xcode projects are Xcode 3.2 compatible.
			 */
			fact 'Xcode compatibility version' {
				val project = projectFactory.create('/foo/bar')
				project.compatibilityVersion should be 'Xcode 3.2'
			}
			
			/**
			 * TODO find out what this is intended for.
			 */
			fact 'Development region' {
				val project = projectFactory.create('/foo/bar')
				project.developmentRegion should be 'English'
			}
			
			/**
			 * TODO find out what this is intened for.
			 */
			fact 'Known regions' {
				val project = projectFactory.create('/foo/bar')
				project.knownRegions should contain 'en'
			}
			
			/**
			 * TODO find out what this is intended for. 
			 */
			fact 'Scanned for encodings' {
				val project = projectFactory.create('/foo/bar')
				project.hasScannedForEncodings should be false
			}
			
		}
	}
	
	context 'Project structure' {
		
		/**
		 * A project is made up of a number of groups. Some of these groups have a special meaning.
		 */
		context 'Groups' {
			
			/**
			 * The main group usually is equivalent with the project root.
			 */
			fact 'A project has one main group' {
				val project = projectFactory.create('/foo/bar')
				project.mainGroup should not be null
			}
			
			/**
			 * Groups can be nested. When a nested group is created using a path, this path will be relative to the
			 * path of the parnet group. If a group is created with a name instead of a path, its location will be
			 * the same as the parents group.
			 */
			fact 'Groups can be nested' {
				val project = projectFactory.create('/foo/bar')
				val mainGroup = project.mainGroup
				
				val fooGroup = mainGroup.createGroup('FooGroup'.toPath)
				fooGroup.path.toString should be 'FooGroup'
				
				val barGroup = fooGroup.createGroup('BarGroup'.toPath)
				barGroup.path.toString should be 'BarGroup'
				barGroup.parentGroup should be fooGroup
				
				val bazGroup = barGroup.createGroup('BazGroup')
				bazGroup.path.toString should be ''
				bazGroup.groupName should be 'BazGroup' 
			}
			
			context 'The main source group' {
				/** 
				 * The main group usually contains a group with the same name as the project name. This group
				 * contains most of the (non-test) source code files that make up a project. 
				 */
				fact 'The main group contains a group for the main source files' {
					val project = projectFactory.create('/foo/bar')
					val mainGroup = project.mainGroup 
					
					val foobarProjectGroup = mainGroup.createGroup('FooBarProject'.toPath)
					foobarProjectGroup should not be null
					foobarProjectGroup.path should not be null
					foobarProjectGroup.path.toString should be 'FooBarProject'
				}
				
				/**
				 * When creating a new Xcode project, the main source group usually contains a virtual group named
				 * `Supporting Files`.
				 */
				fact 'Supporting Files' {
					val project = projectFactory.create('/foo/bar')
					val mainGroup = project.mainGroup 
					
					val foobarProjectGroup = mainGroup.createGroup('FooBarProject'.toPath)
					val supportingfilesGroup = foobarProjectGroup.createGroup('Supporting Files')
					supportingfilesGroup.path.toString should be ''
					supportingfilesGroup.groupName should be 'Supporting Files'					
				}
			}
			
			context 'The unit tests source group' {
				/**
				 * If the project uses unit tests, the test files usually are contained in a group
				 * named `<projectname>Tests`.
				 */			
				fact 'The main group contains a group for the unit test source files' {
					val project = projectFactory.create('/foo/bar')
					val mainGroup = project.mainGroup 
					
					val foobartestsGroup = mainGroup.createGroup('FooBarProjectTests'.toPath)
					foobartestsGroup should not be null
					foobartestsGroup.path should not be null
					foobartestsGroup.path.toString should be 'FooBarProjectTests'
				}
			}
			
			context 'The frameworks group'{
				/**
				 * Almost any project makes use of a number of frameworks, which are grouped into a group
				 * named `Frameworks`. This group has no physical representation on disc, which is why 
				 * its `path` property should be empty whereas the `groupName` should be `Frameworks`. 
				 */
				fact 'The main project contains a group for the frameworks' {
					val project = projectFactory.create('/foo/bar')
					val mainGroup = project.mainGroup
					
					val foobarframeworksGroup = mainGroup.createGroup('Frameworks')
					foobarframeworksGroup should not be null
					foobarframeworksGroup.groupName should not be null
					foobarframeworksGroup.groupName should be 'Frameworks'
					foobarframeworksGroup.path.toString should be ''
				}
			}
			
			context 'The products group' {
				/**
				 * The outcome of the build process is defined in the `Products` group. As well as the
				 * `Frameworks` group, this group does not have a physical representation on disc and thus does
				 * not have a `path` assigned.
				 * 
				 * As this group is of vital interest, it will be created when the project is created.
				 */
				fact 'The main group contains a group for the products of the build process' {
					val project = projectFactory.create('/foo/bar')
					
					val productsGroup = project.productsGroup
					productsGroup should not be null
					productsGroup.productsGroup should be true
					productsGroup.groupName should not be null
					productsGroup.groupName should be 'Products'
					productsGroup.path.toString should be ''
				}
				
				/**
				 * 
				 */
				fact 'The products group contains references to the binary output files of the build process' {
					val project = projectFactory.create('/foo/bar')
					
					val productsGroup = project.productsGroup
					
					val appFile = productsGroup.createAppFile('FooBar.app'.toPath)
					appFile.sourceTree should be SourceTree::BUILT_PRODUCTS_DIR
					
					val octestFile = productsGroup.createOCTestFile('FooBarTests.octest'.toPath)
					octestFile.sourceTree should be SourceTree::BUILT_PRODUCTS_DIR					
				}
				
			}
			
		}
		
		context 'Files' {
			
			/**
			 * Files are grouped into groups, each file belonging to one group. Adding a file to a group
			 * also adds a file reference to the project itself. In addition, a build file reference will
			 * be created for all files that pass the build process.
			 * 
			 * TODO: check if files can be added to more than just one group.
			 */
			fact 'Files belong to a group' {
				val project = projectFactory.create('/foo/bar')
				val mainGroup = project.mainGroup 
				val group = mainGroup.createGroup('FooBarProject'.toPath)
				
				val foobarFile = group.createModuleFile('FooBar.h'.toPath)
				foobarFile should not be null
				foobarFile.path.toString should be 'FooBar.h'
				
				group.files.size should be 1
				group.files should contain foobarFile
				
				project.files.size should be 1
				project.files should contain foobarFile
			}
			
			/**
			 * A number of file types are considered *build files*. 
			 * 
			 * The following file types belong to this category:
			 * 
			 * - module files (`.m`)
			 * - framework wrappers
			 * 
			 * The following file types are *not* build files:
			 * 
			 * - header files (`.h`)
			 */
			fact 'Certain file types are considered build files' {
				val project = projectFactory.create('/foo/bar')
				val mainGroup = project.mainGroup 
				val group = mainGroup.createGroup('FooBarProject'.toPath)
				
				val moduleFile = group.createModuleFile('FooBar.m'.toPath)
				moduleFile.buildFile should be true
				
				val headerFile = group.createHeaderFile('FooBar.h'.toPath)
				headerFile.buildFile should be false
				
				val frameworkWrapper = group.createFrameworkFile('System/Library/Frameworks/UIKit.framework'.toPath)
				frameworkWrapper.buildFile should be true
			}
		}
	}
	
	context 'Configuration Management' {
		
		/**
		 * A project has several targets.
		 */		
		context 'Targets' {
			
			/**
			 * Targets can be created using a number of factory methods on an `XcodeProject`.
			 */
			context 'Creating a target' {
				
				/**
				 * The outcome of an application target is an app.
				 */
				fact 'Creating an application target' {
					val project = projectFactory.create('/foo/bar')
					val target = project.createApplicationTarget('FooBarProject')
					target should not be null
					target.productType should be ProductType::APPLICATION
				}
				
				/**
				 * The outcome of a bundle target is a bundle. Bundle targets are used to create test bundles.
				 * TODO: Check if they also are used to create library bundles.
				 */
				fact 'Creating a bundle target' {
					val project = projectFactory.create('/foo/bar')
					val target = project.createBundleTarget('FooBarProjectTests')
					target should not be null
					target.productType should be ProductType::BUNDLE
				}
				
			}
			
			context 'Naming' {
				
				/**
				 * The target name will be displayed in the *Target* section in the Xcode target editor.
				 */
				fact 'A target has a name' {
					val project = projectFactory.create('/foo/bar')
					val target = project.createApplicationTarget('FooBarProject')
					target.name should be 'FooBarProject'
				}
				
				/**
				 * A target has a product name, but it is not quite clear what this is intended for, as
				 * the name of the target will be displayed in the *Target* section of the target editor
				 * and the product name does not seem to have any influence on any other part of the UI.
				 */
				fact 'A target has a product name' {
					val project = projectFactory.create('/foo/bar')
					val target = project.createApplicationTarget('FooBarProject')
					target.productName should be 'FooBarProject'
				}
			}
			
			/**
			 * A target can have several build phases.
			 */
			context 'Build phases' {
				
				/**
				 * The source build phase defines which source code files will be compiled.
				 */
				context 'Source build phase' {
					
					fact 'Each target should have a source build phase' {
						val project = projectFactory.create('/foo/bar')
						val target = project.createApplicationTarget('FooBarProject')
						target.sourceBuildPhase should not be null
					}
					
					/**
					 * Only source code files will be compiled. Adding non-source code files to the source build
					 * phase is prevented by the API.
					 */
					fact 'Source code files will only be compiled if they are listed in the source build phase' {
						val project = projectFactory.create('/foo/bar')
						val target = project.createApplicationTarget('FooBarProject')
						val sourceBuildPhase = target.sourceBuildPhase
						sourceBuildPhase should not be null
						
						val mainGroup = project.mainGroup 
						val group = mainGroup.createGroup('FooBarProject'.toPath)
						
						val moduleFile = group.createModuleFile('FooBar.m'.toPath)
						sourceBuildPhase.add(moduleFile)
						val headerFile = group.createHeaderFile('FooBar.h'.toPath)
						sourceBuildPhase.add(headerFile)
						val frameworkWrapper = group.createFrameworkFile('System/Library/Frameworks/UIKit.framework'.toPath)
						sourceBuildPhase.add(frameworkWrapper)
						val datamodelFile = group.createDatamodelFile('FooBarProject.xcdatamodeld'.toPath)
						sourceBuildPhase.add(datamodelFile)
						
						sourceBuildPhase.files.size should be 2
						sourceBuildPhase.files should contain moduleFile
						sourceBuildPhase.files should contain datamodelFile
						sourceBuildPhase.files should not contain headerFile
					}
					
				}

				/**
				 * The framework build phase defines which frameworks will be linked with the binary.
				 */
				context 'Framework build phase' {
					
					fact 'A target can have one frameworks build phase' {
						val project = projectFactory.create('/foo/bar')
						val target = project.createApplicationTarget('FooBarProject')
						val frameworkBuildPhase = target.frameworkBuildPhase
						frameworkBuildPhase should not be null
					}
					
					fact 'The frameworks build phase can only contain frameworks' {
						val project = projectFactory.create('/foo/bar')
						val target = project.createApplicationTarget('FooBarProject')
						val frameworkBuildPhase = target.frameworkBuildPhase
						
						val mainGroup = project.mainGroup 
						val group = mainGroup.createGroup('FooBarProject'.toPath)
						
						val moduleFile = group.createModuleFile('FooBar.m'.toPath)
						frameworkBuildPhase.add(moduleFile)
						val headerFile = group.createHeaderFile('FooBar.h'.toPath)
						frameworkBuildPhase.add(headerFile)
						val frameworkWrapper = group.createFrameworkFile('System/Library/Frameworks/UIKit.framework'.toPath)
						frameworkBuildPhase.add(frameworkWrapper)
						val datamodelFile = group.createDatamodelFile('FooBarProject.xcdatamodeld'.toPath)
						frameworkBuildPhase.add(datamodelFile)
						
						frameworkBuildPhase.files.size should be 1
						frameworkBuildPhase.files should contain frameworkWrapper
						frameworkBuildPhase.files should not contain moduleFile
					}
					
					fact 'Frameworks are either required or optional' {
						val project = projectFactory.create('/foo/bar')
						val target = project.createApplicationTarget('FooBarProject')
						val frameworkBuildPhase = target.frameworkBuildPhase
						
						val mainGroup = project.mainGroup 
						val group = mainGroup.createGroup('FooBarProject'.toPath)
						
						val frameworkWrapper = group.createFrameworkFile('System/Library/Frameworks/UIKit.framework'.toPath)
						frameworkBuildPhase.add(frameworkWrapper)
						frameworkWrapper.required should be true
						
						frameworkWrapper.required = false
						frameworkWrapper.required should be false
					}
					
				}				
			}
			
		}
		
	}

}