Feature: Boot Animation

    Scenario: The updater is interrupted
        Given An OS which has booted before and gone through overture
          And an update has been started, but interrupted
         When The OS is booted
          And An image has not been set by `kano-boot-splash-cli set <image.png>`
         Then The interruption warning image displays
          And The interruption warning image is removed before the dashboard startup animation

    Scenario: The updater completes
        Given An OS which has booted before and gone through overture
          And an update has been run and goes to completion
         When The OS is booted
          And An image has not been set by `kano-boot-splash-cli set <image.png>`
         Then The boot animation displays
          And The boot animation stops before the dashboard startup animation

