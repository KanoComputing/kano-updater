#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg


stage ('Build') {
    build_deb_pkg 'kano-updater', env.BRANCH_NAME, 'scratch'
}
